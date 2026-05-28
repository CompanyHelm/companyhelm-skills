import assert from 'node:assert/strict';
import test from 'node:test';
import {
  chatUrlFromAboutData,
  internalUserIdFromAboutData,
  isIntendedDirectChatUrl,
  normalizeUsername,
} from '../scripts/chat_url.mjs';

test('normalizes Reddit username variants', () => {
  assert.equal(normalizeUsername(' u/Example_User '), 'Example_User');
});

test('builds Reddit chat target from about.json data.id instead of data.name', () => {
  const aboutData = { id: 'jb1wd', name: 'KIng_Samosa' };
  assert.equal(internalUserIdFromAboutData(aboutData), 't2_jb1wd');
  assert.equal(chatUrlFromAboutData(aboutData), 'https://chat.reddit.com/user/t2_jb1wd');
});

test('does not double-prefix t2 ids', () => {
  assert.equal(internalUserIdFromAboutData({ id: 't2_abc123' }), 't2_abc123');
});

test('recognizes intended direct chat URLs and room redirects', () => {
  assert.equal(
    isIntendedDirectChatUrl('https://www.reddit.com/chat/user/t2_jb1wd', 'https://chat.reddit.com/user/t2_jb1wd'),
    true,
  );
  assert.equal(
    isIntendedDirectChatUrl('https://www.reddit.com/chat/room/!abc%3Areddit.com', 'https://chat.reddit.com/user/t2_jb1wd'),
    true,
  );
  assert.equal(
    isIntendedDirectChatUrl('https://www.reddit.com/chat/user/t2_other', 'https://chat.reddit.com/user/t2_jb1wd'),
    false,
  );
});
