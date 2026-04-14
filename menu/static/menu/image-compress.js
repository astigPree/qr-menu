const MAX_IMAGE_SIZE = 1024 * 1024;
const MAX_IMAGE_DIMENSION = 1600;
const IMAGE_QUALITIES = [0.85, 0.75, 0.65, 0.55];

function getSafeImageName(fileName, extension) {
    const baseName = fileName
        .replace(/\.[^/.]+$/, "")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "") || "image";
    return `${baseName}.${extension}`;
}

function setCompressionStatus(input, message, status = "info") {
    let statusEl = input.parentElement.querySelector(".image-compress-status");
    if (!statusEl) {
        statusEl = document.createElement("small");
        statusEl.className = "image-compress-status";
        input.insertAdjacentElement("afterend", statusEl);
    }
    statusEl.textContent = message;
    statusEl.dataset.status = status;
}

function canvasToBlob(canvas, mimeType, quality) {
    return new Promise((resolve) => {
        canvas.toBlob(resolve, mimeType, quality);
    });
}

function loadImage(file) {
    return new Promise((resolve, reject) => {
        const image = new Image();
        image.onload = () => resolve(image);
        image.onerror = () => reject(new Error("Unable to read image."));
        image.src = URL.createObjectURL(file);
    });
}

async function compressImage(file) {
    if (!file.type.startsWith("image/")) {
        return file;
    }

    const image = await loadImage(file);
    const scale = Math.min(
        1,
        MAX_IMAGE_DIMENSION / image.naturalWidth,
        MAX_IMAGE_DIMENSION / image.naturalHeight
    );
    const width = Math.max(1, Math.round(image.naturalWidth * scale));
    const height = Math.max(1, Math.round(image.naturalHeight * scale));
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");

    canvas.width = width;
    canvas.height = height;
    context.drawImage(image, 0, 0, width, height);
    URL.revokeObjectURL(image.src);

    const mimeType = "image/webp";
    let bestFile = file;

    for (const quality of IMAGE_QUALITIES) {
        const blob = await canvasToBlob(canvas, mimeType, quality);
        if (!blob) {
            continue;
        }
        const compressedFile = new File(
            [blob],
            getSafeImageName(file.name, "webp"),
            {
                type: mimeType,
                lastModified: Date.now(),
            }
        );
        bestFile = compressedFile;
        if (compressedFile.size <= MAX_IMAGE_SIZE) {
            break;
        }
    }

    return bestFile.size < file.size ? bestFile : file;
}

function replaceInputFile(input, file) {
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    input.files = dataTransfer.files;
}

document.querySelectorAll('input[type="file"][accept*="image"], input[type="file"][name*="image"], input[type="file"][name="logo"]').forEach((input) => {
    input.addEventListener("change", async () => {
        const file = input.files && input.files[0];
        if (!file) {
            return;
        }

        setCompressionStatus(input, "Compressing image before upload...");
        input.disabled = true;

        try {
            const compressedFile = await compressImage(file);
            replaceInputFile(input, compressedFile);
            const sizeMb = (compressedFile.size / 1024 / 1024).toFixed(2);
            setCompressionStatus(input, `Ready to upload: ${sizeMb} MB`, compressedFile.size <= MAX_IMAGE_SIZE ? "success" : "warning");
        } catch (error) {
            setCompressionStatus(input, "Image compression failed. Original image will be used.", "error");
        } finally {
            input.disabled = false;
        }
    });
});

document.querySelectorAll('form[enctype="multipart/form-data"]').forEach((form) => {
    form.addEventListener("submit", async (event) => {
        const imageInputs = Array.from(form.querySelectorAll('input[type="file"]')).filter((input) => {
            const file = input.files && input.files[0];
            return file && file.type.startsWith("image/");
        });

        if (!imageInputs.length || form.dataset.compressedSubmit === "true") {
            return;
        }

        event.preventDefault();
        form.dataset.compressedSubmit = "true";

        try {
            for (const input of imageInputs) {
                const file = input.files[0];
                setCompressionStatus(input, "Compressing image before upload...");
                const compressedFile = await compressImage(file);
                replaceInputFile(input, compressedFile);
                const sizeMb = (compressedFile.size / 1024 / 1024).toFixed(2);
                setCompressionStatus(input, `Ready to upload: ${sizeMb} MB`, compressedFile.size <= MAX_IMAGE_SIZE ? "success" : "warning");
            }

            const response = await fetch(form.action || window.location.href, {
                method: form.method || "POST",
                body: new FormData(form),
                credentials: "same-origin",
            });

            if (response.redirected) {
                window.location.href = response.url;
                return;
            }

            const html = await response.text();
            document.open();
            document.write(html);
            document.close();
        } catch (error) {
            imageInputs.forEach((input) => {
                setCompressionStatus(input, "Image compression failed. Original image will be used.", "error");
            });
            form.submit();
        }
    });
});
