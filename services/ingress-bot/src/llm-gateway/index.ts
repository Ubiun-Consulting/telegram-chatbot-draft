import { OpenAIAdapter } from './adapters/openai';
import { AnthropicAdapter } from './adapters/anthropic';
import { OllamaAdapter } from './adapters/ollama';

export interface LLMAdapter {
  chat(opts: any): Promise<any>;
  embed(texts: string[]): Promise<number[][]>;
}

export function getLLM(): LLMAdapter {
  const provider = process.env.LLM_PROVIDER;
  
  switch (provider) {
    case 'openai':
      return new OpenAIAdapter();
    case 'anthropic':
      return new AnthropicAdapter();
    case 'ollama':
      return new OllamaAdapter();
    default:
      throw new Error(`Unknown LLM_PROVIDER: ${provider}`);
  }
} 