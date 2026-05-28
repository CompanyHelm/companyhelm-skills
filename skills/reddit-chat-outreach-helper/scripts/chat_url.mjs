export function normalizeUsername(username) {
  return String(username || '').trim().replace(/^u\//i, '');
}

export function internalUserIdFromAboutData(data) {
  const id = data?.id || '';
  if (!id) {
    return '';
  }
  return id.startsWith('t2_') ? id : `t2_${id}`;
}

export function chatUrlFromInternalUserId(internalUserId) {
  if (!internalUserId) {
    return '';
  }
  return `https://chat.reddit.com/user/${encodeURIComponent(internalUserId)}`;
}

export function chatUrlFromAboutData(data) {
  return chatUrlFromInternalUserId(internalUserIdFromAboutData(data));
}

export function isIntendedDirectChatUrl(finalUrl, chatUrl) {
  const finalValue = String(finalUrl || '');
  const expected = String(chatUrl || '');
  if (!finalValue) {
    return false;
  }
  if (/\/chat\/room\//.test(finalValue)) {
    return true;
  }
  if (!expected) {
    return /\/chat\/user\/t2_[^/?#]+/i.test(finalValue);
  }
  try {
    const expectedPath = new URL(expected).pathname.replace(/^\/user\//, '/chat/user/');
    const finalPath = new URL(finalValue).pathname;
    return finalPath === expectedPath;
  } catch {
    return /\/chat\/user\/t2_[^/?#]+/i.test(finalValue);
  }
}
