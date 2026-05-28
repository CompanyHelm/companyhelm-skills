#!/usr/bin/env node
import fs from 'fs';
import { chromium } from 'playwright';
import { isIntendedDirectChatUrl } from './chat_url.mjs';

class SendChatCommand {
  static run = async () => {
    const command = new SendChatCommand(process.argv.slice(2));
    const result = await command.execute();
    console.log(command.output(result));
    process.exit(result.ok ? 0 : 1);
  };

  constructor(argv) {
    this.chatUrl = '';
    this.message = '';
    this.cdpUrl = 'http://127.0.0.1:9222';
    this.json = false;
    this.parse(argv);
  }

  parse(argv) {
    for (let index = 0; index < argv.length; index += 1) {
      const value = argv[index];
      if (value === '--chat-url') {
        this.chatUrl = argv[index + 1] || '';
        index += 1;
      } else if (value === '--message') {
        this.message = argv[index + 1] || '';
        index += 1;
      } else if (value === '--message-file') {
        const filePath = argv[index + 1] || '';
        this.message = fs.readFileSync(filePath, 'utf8');
        index += 1;
      } else if (value === '--cdp-url') {
        this.cdpUrl = argv[index + 1] || this.cdpUrl;
        index += 1;
      } else if (value === '--json') {
        this.json = true;
      }
    }
    if (!this.chatUrl) {
      throw new Error('Missing required --chat-url');
    }
    if (!this.message.trim()) {
      throw new Error('Missing required message content');
    }
  }

  async execute() {
    const browser = await chromium.connectOverCDP(this.cdpUrl);
    const context = browser.contexts()[0] || await browser.newContext();
    const page = await context.newPage();
    const result = {
      ok: false,
      status: 'failed',
      chatUrl: this.chatUrl,
      finalUrl: '',
      title: '',
      verificationMethod: '',
      reason: '',
    };

    try {
      await page.goto(this.chatUrl, { waitUntil: 'domcontentloaded', timeout: 45000 });
      await page.waitForTimeout(7000);
      result.finalUrl = page.url();
      result.title = await page.title();
      const initialText = await page.locator('body').innerText().catch(() => '');
      if (this.isBlocked(initialText)) {
        result.status = 'blocked';
        result.reason = 'captcha or human verification gate';
        return result;
      }

      const composer = page.locator('textarea[aria-label="Write message"], textarea[placeholder="Message"], [role="textbox"][aria-label="Write message"]').first();
      await composer.waitFor({ state: 'visible', timeout: 20000 });
      await composer.click();
      await composer.fill(this.message);
      await page.waitForTimeout(800);

      const sendButton = page.locator('button[aria-label="Send message"], [role="button"][aria-label="Send message"]').first();
      if (await sendButton.count()) {
        await sendButton.waitFor({ state: 'visible', timeout: 10000 });
        await page.waitForFunction(
          (selector) => {
            const button = document.querySelector(selector);
            return button && !button.disabled && button.getAttribute('aria-disabled') !== 'true';
          },
          'button[aria-label="Send message"], [role="button"][aria-label="Send message"]',
          { timeout: 10000 },
        );
        await sendButton.click();
      } else {
        await page.keyboard.press('Enter');
      }

      await page.waitForTimeout(6000);
      const finalText = await page.locator('body').innerText().catch(() => '');
      const composerValue = await composer.inputValue().catch(() => '');
      const exactTextMatches = await page.getByText(this.message, { exact: true }).count().catch(() => 0);

      if (exactTextMatches > 0) {
        result.ok = true;
        result.status = 'sent';
        result.verificationMethod = 'exact-message-visible';
        return result;
      }
      if (composerValue === '' && this.isDirectRoom(result.finalUrl, this.chatUrl)) {
        result.ok = true;
        result.status = 'sent';
        result.verificationMethod = 'composer-cleared-in-intended-direct-chat';
        return result;
      }
      if (this.isBlocked(finalText)) {
        result.status = 'blocked';
        result.reason = 'captcha or human verification gate after composer open';
        return result;
      }
      const noChatReason = this.findNoChatReason(finalText);
      if (noChatReason) {
        result.status = 'no_chat';
        result.reason = noChatReason;
        return result;
      }

      result.status = 'failed';
      result.reason = 'message not visible after send';
      return result;
    } catch (error) {
      result.status = 'failed';
      result.reason = this.shortReason(error);
      return result;
    } finally {
      await page.close().catch(() => {});
      await browser.close().catch(() => {});
    }
  }

  isBlocked(text) {
    return /captcha|verify you are human|human verification|challenge/i.test(text);
  }

  isDirectRoom(url, expectedUrl = '') {
    return isIntendedDirectChatUrl(url, expectedUrl);
  }

  findNoChatReason(text) {
    const match = text.match(/unable to invite[^.\n]*|not allowed to send messages[^.\n]*|can.?t send messages[^.\n]*|cannot be invited[^.\n]*|doesn.?t accept direct messages[^.\n]*/i);
    return match ? match[0].replace(/\s+/g, ' ').trim().slice(0, 180) : '';
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
      return `${result.status}: ${result.verificationMethod}`;
    }
    return `${result.status}: ${result.reason}`;
  }
}

await SendChatCommand.run();
