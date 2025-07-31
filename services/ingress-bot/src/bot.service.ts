import { Injectable, OnModuleInit } from '@nestjs/common';
import { Telegraf } from 'telegraf';
import { getLLM } from './llm-gateway';
import * as fs from 'fs/promises';
import axios from 'axios';

export interface ChatOptions {
  prompt: string;
  model?: string;
  stream?: boolean;
  max_tokens?: number;
  temperature?: number;
}

export interface LLMResponse {
  id: string;
  answer: string;
  tokens: number;
  usage_usd: number;
}

@Injectable()
export class BotService implements OnModuleInit {
  private bot: Telegraf;
  private llm: any;

  async onModuleInit() {
    this.bot = new Telegraf(process.env.TELEGRAM_TOKEN!);
    this.llm = getLLM();

    this.bot.on('text', async (ctx) => {
      try {
        const question = ctx.message.text;
        const userId = ctx.from?.id;

        // Get relevant document chunks
        const retrievalResponse = await axios.get(
          `${process.env.RETRIEVAL_URL}/search`,
          {
            params: {
              q: question,
              k: 5
            }
          }
        );

        const documents = retrievalResponse.data.documents || [];
        const chunks = documents.map((doc: any) => doc.text).join('\n---\n');

        // Build prompt with system directive
        const basePrompt = await fs.readFile('prompts/base_prompt.txt', 'utf-8');
        const prompt = `${basePrompt}\n\n${chunks}\n\nUser: ${question}`;

        // Get LLM response
        const response = await this.llm.chat({
          prompt,
          model: process.env.LLM_MODEL || 'gpt-4o-mini',
          stream: false,
          max_tokens: 512,
          temperature: 0.7
        });

        // Reply to user
        await ctx.reply(response.answer);

        // Log audit
        await this.logAudit(userId, question, response);

      } catch (error) {
        console.error('Error processing message:', error);
        await ctx.reply('Sorry, I encountered an error. Please try again.');
      }
    });

    await this.bot.launch();
    console.log('Bot started successfully');
  }

  private async logAudit(userId: number | undefined, question: string, response: LLMResponse) {
    try {
      await axios.post(process.env.AUDIT_URL!, {
        user_id: userId,
        question,
        answer: response.answer,
        tokens: response.tokens,
        usage_usd: response.usage_usd,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Failed to log audit:', error);
    }
  }
} 