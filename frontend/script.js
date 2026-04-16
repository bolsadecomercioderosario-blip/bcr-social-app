let sessionData = {
    session_id: null,
    pdf_path: null
};

document.getElementById('preProcessBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('pdfInput');
    if (!fileInput.files.length) {
        alert("Por favor, selecciona un documento PDF.");
        return;
    }

    const btn = document.getElementById('preProcessBtn');
    const loader = document.getElementById('loader');
    const step2 = document.getElementById('step2');
    const results = document.getElementById('results');

    btn.disabled = true;
    loader.style.display = 'block';
    results.style.display = 'none';
    step2.style.display = 'none';

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('http://127.0.0.1:8002/api/pre-procesar', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            alert("Error: " + data.error);
        } else {
            sessionData.session_id = data.session_id;
            sessionData.pdf_path = data.pdf_path;
            
            document.getElementById('titleInput').value = data.title;
            document.getElementById('pdfPreviewImg').src = `http://127.0.0.1:8002${data.preview_url}?t=${new Date().getTime()}`;
            step2.style.display = 'block';
        }
    } catch (error) {
        alert("Ocurrió un error de red: " + error.message);
    } finally {
        btn.disabled = false;
        loader.style.display = 'none';
    }
});

document.getElementById('generateBtn').addEventListener('click', async () => {
    const title = document.getElementById('titleInput').value;
    const btn = document.getElementById('generateBtn');
    const loader = document.getElementById('loader');
    const results = document.getElementById('results');

    btn.disabled = true;
    loader.style.display = 'block';

    const formData = new FormData();
    formData.append('session_id', sessionData.session_id);
    formData.append('pdf_path', sessionData.pdf_path);
    formData.append('title', title);

    try {
        const response = await fetch('http://127.0.0.1:8002/api/generar', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            alert("Error: " + data.error);
        } else {
            document.getElementById('twitterText').value = data.twitter_text;
            
            document.getElementById('comunicadoImg').src = `http://127.0.0.1:8002${data.comunicado_img}?t=${new Date().getTime()}`;
            document.getElementById('downloadComunicadoBtn').href = `http://127.0.0.1:8002${data.comunicado_url}`;
            
            document.getElementById('storyImg').src = `http://127.0.0.1:8002${data.story_img}?t=${new Date().getTime()}`;
            document.getElementById('downloadStoryBtn').href = `http://127.0.0.1:8002${data.story_url}`;

            results.style.display = 'grid';
            window.scrollTo({ top: results.offsetTop, behavior: 'smooth' });
        }
    } catch (error) {
        alert("Ocurrió un error: " + error.message);
    } finally {
        btn.disabled = false;
        loader.style.display = 'none';
    }
});

document.getElementById('copyXBtn').addEventListener('click', () => {
    const text = document.getElementById('twitterText');
    text.select();
    navigator.clipboard.writeText(text.value);
    const originalText = document.getElementById('copyXBtn').innerText;
    document.getElementById('copyXBtn').innerText = "¡Copiado!";
    setTimeout(() => {
        document.getElementById('copyXBtn').innerText = originalText;
    }, 2000);
});
