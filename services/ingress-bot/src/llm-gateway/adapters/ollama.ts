import axios from 'axios';
import { LLMAdapter } from '../index';

export class OllamaAdapter implements LLMAdapter {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.OLLAMA_BASE_URL || 'http://localhost:11434';
  }

  async chat(opts: any) {
    const response = await axios.post(`${this.baseUrl}/api/generate`, {
      model: opts.model || 'llama2',
      prompt: opts.prompt,
      stream: opts.stream || false,
      options: {
        num_predict: opts.max_tokens || 512,
        temperature: opts.temperature || 0.7
      }
    });

    return {
      id: response.data.id || 'ollama-' + Date.now(),
      answer: response.data.response,
      tokens: response.data.eval_count || 0,
      usage_usd: 0 // Local model, no cost
    };
  }

  async embed(texts: string[]): Promise<number[][]> {
    const embeddings = await Promise.all(
      texts.map(async (text) => {
        const response = await axios.post(`${this.baseUrl}/api/embeddings`, {
          model: 'llama2',
          prompt: text
        });
        return response.data.embedding;
      })
    );

    return embeddings;
  }
} 