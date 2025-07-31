import { NestFactory } from '@nestjs/core';
import { BotModule } from './bot.module';

async function bootstrap() {
  const app = await NestFactory.create(BotModule);
  
  // Enable CORS for webhook endpoints
  app.enableCors();
  
  // Health check endpoint
  app.get('/health', (req, res) => {
    res.json({ status: 'ok', service: 'ingress-bot' });
  });
  
  // Telegram webhook endpoint
  app.post('/telegram/webhook', (req, res) => {
    // This will be handled by the BotService
    res.json({ status: 'ok' });
  });
  
  await app.listen(3000);
  console.log('Ingress bot is running on port 3000');
}

bootstrap().catch(err => {
  console.error('Failed to start ingress bot:', err);
  process.exit(1);
}); 