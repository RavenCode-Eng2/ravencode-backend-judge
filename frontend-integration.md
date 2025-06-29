# Integración Frontend - RavenCode Judge API

## 🔗 **Configuración del Frontend**

### **1. Variables de Entorno**
Crea un archivo `.env` en tu frontend:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1
```

### **2. Configuración de Axios/Fetch**
```javascript
// config/api.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_VERSION = import.meta.env.VITE_API_VERSION || 'v1';

export const API_ENDPOINTS = {
  // Problemas
  PROBLEMS: `${API_BASE_URL}/api/${API_VERSION}/problems`,
  PROBLEM_BY_ID: (id) => `${API_BASE_URL}/api/${API_VERSION}/problems/${id}`,
  
  // Submisiones
  SUBMISSIONS: `${API_BASE_URL}/api/${API_VERSION}/submissions`,
  SUBMISSION_BY_ID: (id) => `${API_BASE_URL}/api/${API_VERSION}/submissions/${id}`,
  
  // Autenticación (opcional)
  AUTH_LOGIN: `${API_BASE_URL}/api/${API_VERSION}/auth/login`,
  AUTH_REGISTER: `${API_BASE_URL}/api/${API_VERSION}/auth/register`,
  AUTH_ME: `${API_BASE_URL}/api/${API_VERSION}/auth/me`,
};
```

## 📋 **Servicios API**

### **1. Servicio de Problemas**
```javascript
// services/problemService.js
import { API_ENDPOINTS } from '../config/api';

export const problemService = {
  // Obtener todos los problemas
  async getProblems(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = `${API_ENDPOINTS.PROBLEMS}?${queryString}`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('Error al obtener problemas');
    return response.json();
  },

  // Obtener un problema específico
  async getProblem(id) {
    const response = await fetch(API_ENDPOINTS.PROBLEM_BY_ID(id));
    if (!response.ok) throw new Error('Problema no encontrado');
    return response.json();
  },

  // Crear un nuevo problema (solo admin)
  async createProblem(problemData) {
    const response = await fetch(API_ENDPOINTS.PROBLEMS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(problemData),
    });
    if (!response.ok) throw new Error('Error al crear problema');
    return response.json();
  },
};
```

### **2. Servicio de Submisiones**
```javascript
// services/submissionService.js
import { API_ENDPOINTS } from '../config/api';

export const submissionService = {
  // Enviar código para evaluar
  async submitCode(submissionData) {
    const response = await fetch(API_ENDPOINTS.SUBMISSIONS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(submissionData),
    });
    if (!response.ok) throw new Error('Error al enviar código');
    return response.json();
  },

  // Obtener submisiones del usuario
  async getSubmissions(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const url = `${API_ENDPOINTS.SUBMISSIONS}?${queryString}`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('Error al obtener submisiones');
    return response.json();
  },

  // Obtener una submisión específica
  async getSubmission(id) {
    const response = await fetch(API_ENDPOINTS.SUBMISSION_BY_ID(id));
    if (!response.ok) throw new Error('Submisión no encontrada');
    return response.json();
  },

  // Polling para obtener resultados
  async pollSubmissionResult(submissionId, maxAttempts = 30) {
    for (let i = 0; i < maxAttempts; i++) {
      const submission = await this.getSubmission(submissionId);
      
      if (submission.status !== 'pending' && submission.status !== 'running') {
        return submission;
      }
      
      // Esperar 1 segundo antes del siguiente intento
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    throw new Error('Tiempo de espera agotado');
  },
};
```

## 🎯 **Integración con CodeMirror**

### **1. Componente de Editor**
```javascript
// components/CodeEditor.jsx
import { useEffect, useState } from 'react';
import { EditorView, basicSetup } from 'codemirror';
import { EditorState } from '@codemirror/state';
import { javascript } from '@codemirror/lang-javascript';
import { python } from '@codemirror/lang-python';
import { java } from '@codemirror/lang-java';

const CodeEditor = ({ 
  language = 'python', 
  code = '', 
  onChange,
  readOnly = false 
}) => {
  const [editor, setEditor] = useState(null);

  useEffect(() => {
    if (!editor) return;

    const languageExtension = {
      'python': python(),
      'javascript': javascript(),
      'java': java(),
    }[language] || python();

    const state = EditorState.create({
      doc: code,
      extensions: [
        basicSetup,
        languageExtension,
        EditorView.updateListener.of((update) => {
          if (update.docChanged && onChange) {
            onChange(update.state.doc.toString());
          }
        }),
        EditorView.editable.of(!readOnly),
      ],
    });

    editor.setState(state);
  }, [language, code, readOnly]);

  return (
    <div 
      ref={(el) => {
        if (el && !editor) {
          setEditor(new EditorView({ parent: el }));
        }
      }}
      className="code-editor"
    />
  );
};

export default CodeEditor;
```

### **2. Componente de Problema**
```javascript
// components/ProblemView.jsx
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { problemService, submissionService } from '../services';
import CodeEditor from './CodeEditor';

const ProblemView = () => {
  const { problemId } = useParams();
  const [problem, setProblem] = useState(null);
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    loadProblem();
  }, [problemId]);

  const loadProblem = async () => {
    try {
      const problemData = await problemService.getProblem(problemId);
      setProblem(problemData);
    } catch (error) {
      console.error('Error cargando problema:', error);
    }
  };

  const handleSubmit = async () => {
    if (!code.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      // Enviar código
      const submissionData = await submissionService.submitCode({
        problem_id: parseInt(problemId),
        code: code,
        language: language,
      });

      setSubmission(submissionData);

      // Polling para obtener resultados
      const finalResult = await submissionService.pollSubmissionResult(submissionData.id);
      setResult(finalResult);
    } catch (error) {
      console.error('Error enviando código:', error);
      setResult({ status: 'error', error_message: error.message });
    } finally {
      setLoading(false);
    }
  };

  if (!problem) return <div>Cargando...</div>;

  return (
    <div className="problem-view">
      <div className="problem-header">
        <h1>{problem.title}</h1>
        <span className={`difficulty ${problem.difficulty}`}>
          {problem.difficulty}
        </span>
      </div>

      <div className="problem-description">
        <h3>Descripción</h3>
        <p>{problem.description}</p>
      </div>

      <div className="problem-examples">
        <h3>Ejemplos</h3>
        {problem.test_cases
          .filter(tc => tc.is_sample)
          .map((testCase, index) => (
            <div key={testCase.id} className="example">
              <h4>Ejemplo {index + 1}</h4>
              <div className="input-output">
                <div>
                  <strong>Entrada:</strong>
                  <pre>{testCase.input_data}</pre>
                </div>
                <div>
                  <strong>Salida:</strong>
                  <pre>{testCase.expected_output}</pre>
                </div>
              </div>
            </div>
          ))}
      </div>

      <div className="code-section">
        <div className="code-header">
          <h3>Tu Solución</h3>
          <select 
            value={language} 
            onChange={(e) => setLanguage(e.target.value)}
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
          </select>
        </div>

        <CodeEditor
          language={language}
          code={code}
          onChange={setCode}
        />

        <button 
          onClick={handleSubmit} 
          disabled={loading || !code.trim()}
          className="submit-btn"
        >
          {loading ? 'Evaluando...' : 'Enviar Solución'}
        </button>
      </div>

      {result && (
        <div className={`result ${result.status}`}>
          <h3>Resultado</h3>
          <div className="result-details">
            <p><strong>Estado:</strong> {result.status}</p>
            <p><strong>Puntuación:</strong> {result.score}%</p>
            {result.execution_time && (
              <p><strong>Tiempo:</strong> {result.execution_time.toFixed(3)}s</p>
            )}
            {result.error_message && (
              <p><strong>Error:</strong> {result.error_message}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProblemView;
```

## 🎨 **Estilos CSS Básicos**
```css
/* styles/ProblemView.css */
.problem-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.problem-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.difficulty {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.difficulty.easy { background: #d4edda; color: #155724; }
.difficulty.medium { background: #fff3cd; color: #856404; }
.difficulty.hard { background: #f8d7da; color: #721c24; }

.code-editor {
  border: 1px solid #ddd;
  border-radius: 8px;
  margin: 20px 0;
  height: 400px;
}

.submit-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}

.submit-btn:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.result {
  margin-top: 20px;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid;
}

.result.accepted {
  background: #d4edda;
  border-color: #c3e6cb;
  color: #155724;
}

.result.wrong_answer {
  background: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
}

.result.error {
  background: #f8d7da;
  border-color: #f5c6cb;
  color: #721c24;
}
```

## 🚀 **Próximos Pasos**

1. **Copiar estos archivos** a tu proyecto frontend
2. **Instalar dependencias** de CodeMirror
3. **Configurar rutas** en tu router
4. **Probar la integración**

¿Quieres que te ayude con algún paso específico o tienes alguna duda sobre la implementación? 