chrome.storage.sync.get(["enabled", "strength"], (s) => {
  document.getElementById("enabled").checked = s.enabled !== false;
  document.getElementById("strength").value = s.strength || "standard";
});

document.getElementById("save").onclick = () => {
  chrome.storage.sync.set({
    enabled: document.getElementById("enabled").checked,
    strength: document.getElementById("strength").value,
  });
  window.close();
};
