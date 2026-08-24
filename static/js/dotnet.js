(function () {
    const canvas = document.getElementById('dotnet-canvas');
    if (!canvas || window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        return;
    }

    const ctx = canvas.getContext('2d', { alpha: true });
    if (!ctx) {
        return;
    }

    const canHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    const GRAY = '148, 163, 184';
    const SPACING = 52;
    const CONNECT = 78;
    const CONNECT_HOT = 128;
    const MOUSE_RADIUS = 240;
    const DOT = 1.15;

    const state = {
        points: [],
        cols: 0,
        rows: 0,
        w: 0,
        h: 0,
        dpr: 1,
        mx: -9999,
        my: -9999,
        heat: 0,
        targetHeat: 0,
        t: 0,
        raf: 0
    };

    const dist2 = (ax, ay, bx, by) => {
        const dx = ax - bx;
        const dy = ay - by;
        return dx * dx + dy * dy;
    };

    const resize = () => {
        const dpr = Math.min(window.devicePixelRatio || 1, 1.5);
        const w = window.innerWidth;
        const h = window.innerHeight;
        state.dpr = dpr;
        state.w = w;
        state.h = h;
        canvas.width = Math.floor(w * dpr);
        canvas.height = Math.floor(h * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        const cols = Math.ceil(w / SPACING) + 3;
        const rows = Math.ceil(h / SPACING) + 3;
        state.cols = cols;
        state.rows = rows;
        state.points = [];

        for (let row = 0; row < rows; row += 1) {
            for (let col = 0; col < cols; col += 1) {
                state.points.push({
                    ox: (col - 1) * SPACING + (Math.random() - 0.5) * 10,
                    oy: (row - 1) * SPACING + (Math.random() - 0.5) * 10,
                    phase: Math.random() * Math.PI * 2,
                    amp: 4 + Math.random() * 5,
                    col,
                    row
                });
            }
        }
    };

    const pointAt = (col, row) => {
        if (col < 0 || row < 0 || col >= state.cols || row >= state.rows) {
            return null;
        }
        return state.points[row * state.cols + col];
    };

    const setHover = (on) => {
        state.targetHeat = on ? 1 : 0;
        document.body.classList.toggle('is-dotnet-hot', on);
    };

    const draw = (now) => {
        state.t = now * 0.001;
        state.heat += (state.targetHeat - state.heat) * 0.06;

        const { w, h, points, heat } = state;
        const connect = CONNECT + (CONNECT_HOT - CONNECT) * heat;
        const connect2 = connect * connect;
        const mouseR = MOUSE_RADIUS * (0.72 + heat * 0.45);
        const mouseR2 = mouseR * mouseR;

        ctx.clearRect(0, 0, w, h);

        const positions = points.map((p) => {
            const driftX = Math.sin(state.t * 0.35 + p.phase) * p.amp;
            const driftY = Math.cos(state.t * 0.28 + p.phase * 1.3) * p.amp;
            let x = p.ox + driftX;
            let y = p.oy + driftY;
            const toMouse = dist2(x, y, state.mx, state.my);
            let influence = 0;
            if (toMouse < mouseR2) {
                influence = 1 - Math.sqrt(toMouse) / mouseR;
                const push = influence * influence * (10 + heat * 16);
                const angle = Math.atan2(y - state.my, x - state.mx);
                x += Math.cos(angle) * push;
                y += Math.sin(angle) * push;
            }
            p.x = x;
            p.y = y;
            p.influence = influence;
            return p;
        });

        ctx.lineWidth = 1;
        ctx.lineCap = 'round';

        const neighborOffsets = heat > 0.08
            ? [[1, 0], [0, 1], [1, 1], [-1, 1], [2, 0], [0, 2], [2, 1], [1, 2]]
            : [[1, 0], [0, 1], [1, 1], [-1, 1]];

        for (let i = 0; i < positions.length; i += 1) {
            const a = positions[i];
            for (let n = 0; n < neighborOffsets.length; n += 1) {
                const b = pointAt(a.col + neighborOffsets[n][0], a.row + neighborOffsets[n][1]);
                if (!b) {
                    continue;
                }
                const d2 = dist2(a.x, a.y, b.x, b.y);
                if (d2 > connect2) {
                    continue;
                }
                const proximity = 1 - Math.sqrt(d2) / connect;
                const bloom = Math.max(a.influence, b.influence);
                const alpha = (0.14 + proximity * 0.22) * (0.7 + heat * 0.4) + bloom * 0.5;
                if (alpha < 0.04) {
                    continue;
                }
                ctx.strokeStyle = `rgba(${GRAY}, ${Math.min(alpha, 0.82)})`;
                ctx.beginPath();
                ctx.moveTo(a.x, a.y);
                ctx.lineTo(b.x, b.y);
                ctx.stroke();
            }

            if (heat > 0.12 && a.influence > 0.12) {
                const grab = a.influence * (0.18 + heat * 0.28);
                ctx.strokeStyle = `rgba(${GRAY}, ${grab})`;
                ctx.beginPath();
                ctx.moveTo(state.mx, state.my);
                ctx.lineTo(a.x, a.y);
                ctx.stroke();
            }
        }

        for (let i = 0; i < positions.length; i += 1) {
            const p = positions[i];
            const size = DOT + p.influence * (1.6 + heat * 1.2);
            const alpha = 0.38 + p.influence * 0.5 + heat * 0.1;
            ctx.fillStyle = `rgba(${GRAY}, ${Math.min(alpha, 0.9)})`;
            ctx.beginPath();
            ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
            ctx.fill();
        }

        state.raf = requestAnimationFrame(draw);
    };

    const start = () => {
        document.body.classList.add('has-dotnet');
        resize();

        if (canHover) {
            window.addEventListener('pointermove', (event) => {
                state.mx = event.clientX;
                state.my = event.clientY;
                setHover(true);
            }, { passive: true });

            document.documentElement.addEventListener('mouseleave', () => {
                state.mx = -9999;
                state.my = -9999;
                setHover(false);
            });

            window.addEventListener('blur', () => setHover(false));
        }

        window.addEventListener('resize', resize);
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                cancelAnimationFrame(state.raf);
                state.raf = 0;
            } else if (!state.raf) {
                state.raf = requestAnimationFrame(draw);
            }
        });

        state.raf = requestAnimationFrame(draw);
    };

    start();
})();
