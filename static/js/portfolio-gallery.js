(function () {
    const gallery = document.querySelector('[data-portfolio-gallery]');
    if (!gallery) {
        return;
    }

    const items = Array.from(gallery.querySelectorAll('[data-gallery-item]'));
    if (!items.length) {
        return;
    }

    const lightbox = document.querySelector('[data-gallery-lightbox]');
    if (!lightbox) {
        return;
    }

    const stage = lightbox.querySelector('[data-gallery-stage]');
    const caption = lightbox.querySelector('[data-gallery-caption]');
    const counter = lightbox.querySelector('[data-gallery-counter]');
    const prevBtn = lightbox.querySelector('[data-gallery-prev]');
    const nextBtn = lightbox.querySelector('[data-gallery-next]');
    const closeTargets = lightbox.querySelectorAll('[data-gallery-close]');

    let current = 0;

    function itemPayload(item) {
        return {
            type: item.dataset.galleryType || 'image',
            src: item.dataset.gallerySrc || '',
            caption: item.dataset.galleryCaption || '',
        };
    }

    function render(index) {
        current = (index + items.length) % items.length;
        const item = itemPayload(items[current]);
        stage.replaceChildren();

        if (item.type === 'video') {
            const video = document.createElement('video');
            video.src = item.src;
            video.controls = true;
            video.playsInline = true;
            video.autoplay = true;
            video.className = 'max-h-[80vh] max-w-full rounded-xl bg-black';
            stage.appendChild(video);
        } else if (item.type === 'embed') {
            const frame = document.createElement('iframe');
            frame.src = item.src;
            frame.title = item.caption || 'Project video';
            frame.allow =
                'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
            frame.allowFullscreen = true;
            frame.className = 'w-[min(90vw,960px)] aspect-video rounded-xl bg-black';
            stage.appendChild(frame);
        } else {
            const image = document.createElement('img');
            image.src = item.src;
            image.alt = item.caption || 'Gallery image';
            image.className = 'max-h-[80vh] max-w-full rounded-xl object-contain';
            stage.appendChild(image);
        }

        caption.textContent = item.caption;
        caption.hidden = !item.caption;
        counter.textContent = `${current + 1} / ${items.length}`;
    }

    function open(index) {
        render(index);
        lightbox.hidden = false;
        lightbox.classList.remove('hidden');
        document.body.classList.add('overflow-hidden');
        lightbox.focus();
    }

    function close() {
        lightbox.hidden = true;
        lightbox.classList.add('hidden');
        stage.replaceChildren();
        document.body.classList.remove('overflow-hidden');
    }

    items.forEach((item, index) => {
        item.addEventListener('click', (event) => {
            event.preventDefault();
            open(index);
        });
        item.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                open(index);
            }
        });
    });

    prevBtn.addEventListener('click', () => render(current - 1));
    nextBtn.addEventListener('click', () => render(current + 1));
    closeTargets.forEach((el) => el.addEventListener('click', close));

    lightbox.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            close();
        } else if (event.key === 'ArrowLeft') {
            render(current - 1);
        } else if (event.key === 'ArrowRight') {
            render(current + 1);
        }
    });
})();
