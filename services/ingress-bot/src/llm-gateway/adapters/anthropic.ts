import Anthropic from '@anthropic-ai/sdk';
import { LLMAdapter } from '../index';

export class AnthropicAdapter implements LLMAdapter {
  private client: Anthropic;

  constructor() {
    this.client = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY!
    });
  }

  async chat(opts: any) {
    const response = await this.client.messages.create({
      model: opts.model || 'claude-3-sonnet-20240229',
      max_tokens: opts.max_tokens || 512,
      temperature: opts.temperature || 0.7,
      messages: [{ role: 'user', content: opts.prompt }]
    });

    return {
      id: response.id,
      answer: response.content[0].text,
      tokens: response.usage?.input_tokens + response.usage?.output_tokens || 0,
      usage_usd: this.estimateCost(response)
    };
  }

  async embed(texts: string[]): Promise<number[][]> {
    const embeddings = await Promise.all(
      texts.map(text => 
        this.client.embeddings.create({
          model: 'text-embedding-3',
          input: text
        })
      )
    );

    return embeddings.map(response => response.embedding);
  }

  private estimateCost(response: any): number {
    // Rough cost estimation for Claude
    const inputTokens = response.usage?.input_tokens || 0;
    const outputTokens = response.usage?.output_tokens || 0;
    
    // Claude-3 pricing (approximate)
    const inputCost = inputTokens * 0.000003; // $3 per 1M tokens
    const outputCost = outputTokens * 0.000015; // $15 per 1M tokens
    
    return inputCost + outputCost;
  }
} 