// 净土 Jingtu 内容脚本
// 监听页面，把可疑的评论/帖子文本发给本地分类服务，命中的折叠（可点击恢复）。
const API = "http://127.0.0.1:8000/classify";

let settings = { enabled: true, strength: "standard" };
chrome.storage.sync.get(["enabled", "strength"], (s) => {
  settings = { enabled: s.enabled !== false, strength: s.strength || "standard" };
});
chrome.storage.onChanged.addListener((changes) => {
  if (changes.enabled) settings.enabled = changes.enabled.newValue;
  if (changes.strength) settings.strength = changes.strength.newValue;
});

async function classify(text) {
  try {
    const res = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, strength: settings.strength }),
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null; // 本地服务没启动时不处理
  }
}

function fold(el) {
  el.style.opacity = "0.12";
  el.style.filter = "grayscale(1)";
  el.title = "净土已折叠（疑似负面内容），点击恢复";
  el.dataset.jingtu = "1";
  el.addEventListener(
    "click",
    () => {
      el.style.opacity = "";
      el.style.filter = "";
      el.dataset.jingtu = "0";
    },
    { once: true }
  );
}

// 各平台评论/帖子文本容器选择器（DOM 会变，可按需增改）
const SELECTORS = [
  "#content-text",                                   // YouTube 评论
  "ytd-comment-thread-renderer #content-text",       // YouTube
  "article [data-testid='tweetText']",               // X / Twitter
  "[data-e2e='comment']",                            // TikTok 网页
  "[data-testid='post-content']",                    // Reddit
  ".reply-content",                                  // 知乎
  ".comment-content",                                // B站
];

const seen = new WeakSet();

function scan() {
  if (!settings.enabled) return;
  for (const sel of SELECTORS) {
    document.querySelectorAll(sel).forEach(async (el) => {
      if (seen.has(el) || el.dataset.jingtu) return;
      seen.add(el);
      const text = (el.innerText || "").trim();
      if (!text || text.length > 500) return;
      const result = await classify(text);
      if (result && result.blocked) {
        fold(el.closest("ytd-comment-thread-renderer") || el);
      }
    });
  }
}

const obs = new MutationObserver(() => scan());
obs.observe(document.body, { childList: true, subtree: true });
scan();
