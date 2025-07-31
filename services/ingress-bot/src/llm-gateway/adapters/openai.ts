import OpenAI from 'openai';
import { LLMAdapter } from '../index';

export class OpenAIAdapter implements LLMAdapter {
  private client: OpenAI;

  constructor() {
    this.client = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY!
    });
  }

  async chat(opts: any) {
    const response = await this.client.chat.completions.create({
      model: opts.model || 'gpt-4o-mini',
      messages: [{ role: 'user', content: opts.prompt }],
      max_tokens: opts.max_tokens || 512,
      temperature: opts.temperature || 0.7,
      stream: opts.stream || false
    });

    return {
      id: response.id,
      answer: response.choices[0].message.content,
      tokens: response.usage?.total_tokens || 0,
      usage_usd: this.estimateCost(response)
    };
  }

  async embed(texts: string[]): Promise<number[][]> {
    const response = await this.client.embeddings.create({
      model: 'text-embedding-3-small',
      input: texts
    });

    return response.data.map(item => item.embedding);
  }

  private estimateCost(response: any): number {
    // Rough cost estimation - adjust based on actual pricing
    const model = response.model;
    const tokens = response.usage?.total_tokens || 0;
    
    if (model.includes('gpt-4')) {
      return tokens * 0.00003; // $0.03 per 1K tokens
    } else if (model.includes('gpt-3.5')) {
      return tokens * 0.000002; // $0.002 per 1K tokens
    }
    
    return 0;
  }
} 