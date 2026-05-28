#!/usr/bin/env node
import { chromium } from 'playwright';
import { chatUrlFromAboutData, internalUserIdFromAboutData, normalizeUsername } from './chat_url.mjs';

class ResolveChatTargetCommand {
  static run = async () => {
    const command = new ResolveChatTargetCommand(process.argv.slice(2));
    const result = await command.execute();
    console.log(command.output(result));
    process.exit(result.ok ? 0 : 1);
  };

  constructor(argv) {
    this.username = '';
    this.cdpUrl = 'http://127.0.0.1:9222';
    this.json = false;
    this.parse(argv);
  }

  parse(argv) {
    for (let index = 0; index < argv.length; index += 1) {
      const value = argv[index];
      if (value === '--username') {
        this.username = argv[index + 1] || '';
        index += 1;
      } else if (value === '--cdp-url') {
        this.cdpUrl = argv[index + 1] || this.cdpUrl;
        index += 1;
      } else if (value === '--json') {
        this.json = true;
      }
    }
    if (!this.username) {
      throw new Error('Missing required --username');
    }
  }

  normalizedUsername() {
    return normalizeUsername(this.username);
  }

  async execute() {
    const browser = await chromium.connectOverCDP(this.cdpUrl);
    const context = browser.contexts()[0] || await browser.newContext();
    const page = await context.newPage();
    try {
      const username = this.normalizedUsername();
      const aboutUrl = `https://www.reddit.com/user/${encodeURIComponent(username)}/about.json`;
      await page.goto(aboutUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(1200);
      const bodyText = await page.locator('body').innerText();
      const payload = JSON.parse(bodyText);
      const internalUserId = internalUserIdFromAboutData(payload?.data);
      const displayName = payload?.data?.name || username;
      if (!internalUserId) {
        return {
          ok: false,
          status: 'no_chat',
          username,
          aboutUrl,
          reason: 'missing t2 user id in about.json',
        };
      }
      return {
        ok: true,
        status: 'ok',
        username,
        aboutUrl,
        displayName,
        internalUserId,
        chatUrl: chatUrlFromAboutData(payload?.data),
      };
    } catch (error) {
      return {
        ok: false,
        status: 'failed',
        username: this.normalizedUsername(),
        reason: this.shortReason(error),
      };
    } finally {
      await page.close().catch(() => {});
      await browser.close().catch(() => {});
    }
  }

  shortReason(error) {
    const value = error instanceof Error ? error.message : String(error);
    return value.replace(/\s+/g, ' ').trim().slice(0, 200);
  }

  output(result) {
    if (this.json) {
      return JSON.stringify(result, null, 2);
    }
    if (result.ok) {
      return result.chatUrl;
    }
    return `${result.status}: ${result.reason}`;
  }
}

await ResolveChatTargetCommand.run();
