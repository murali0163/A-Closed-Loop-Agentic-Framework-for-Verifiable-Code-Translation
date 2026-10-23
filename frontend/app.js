const sourceInput = document.querySelector('#source');
const translateButton = document.querySelector('#translate-button');
const output = document.querySelector('#output code');
const status = document.querySelector('#result-status');
const meta = document.querySelector('#result-meta');
const count = document.querySelector('#source-count');

function updateCount() {
  const lines = sourceInput.value ? sourceInput.value.split('\n').length : 0;
  count.textContent = `${lines} ${lines === 1 ? 'line' : 'lines'}`;
}

sourceInput.addEventListener('input', updateCount);
updateCount();

document.querySelector('#clear-button').addEventListener('click', () => {
  sourceInput.value = '';
  output.textContent = '// Your verified Rust translation will appear here.';
  status.textContent = 'READY';
  status.className = 'status-pill';
  meta.textContent = 'Ready when you are';
  updateCount();
  sourceInput.focus();
});

document.querySelector('#copy-button').addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(output.textContent);
    meta.textContent = 'Copied to clipboard';
  } catch {
    meta.textContent = 'Clipboard unavailable in this browser';
  }
});

translateButton.addEventListener('click', async () => {
  const source = sourceInput.value.trim();
  if (!source) {
    status.textContent = 'ADD SOURCE';
    status.className = 'status-pill error';
    meta.textContent = 'Paste Python code to start';
    sourceInput.focus();
    return;
  }

  translateButton.disabled = true;
  translateButton.querySelector('span:nth-child(2)').textContent = 'Translating…';
  status.textContent = 'WORKING';
  status.className = 'status-pill';
  meta.textContent = 'Translation and verification in progress';
  output.textContent = '// Translating and verifying your code…';

  try {
    const response = await fetch('/api/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source, file_name: 'browser_input.py' }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'The translation request failed.');
    output.textContent = result.rust_code || '// No Rust code was returned.';
    status.textContent = result.success ? 'VERIFIED' : 'CHECK RESULT';
    status.className = `status-pill ${result.success ? 'success' : 'error'}`;
    meta.textContent = result.success
      ? `Verified in ${result.iterations} ${result.iterations === 1 ? 'iteration' : 'iterations'}`
      : (result.error || `Verification did not pass after ${result.iterations} iterations`);
  } catch (error) {
    output.textContent = `// ${error.message}`;
    status.textContent = 'ERROR';
    status.className = 'status-pill error';
    meta.textContent = 'Check that the backend server is running';
  } finally {
    translateButton.disabled = false;
    translateButton.querySelector('span:nth-child(2)').textContent = 'Translate to Rust';
  }
});
