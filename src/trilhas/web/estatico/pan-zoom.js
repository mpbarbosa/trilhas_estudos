// Mover e ampliar o grafo. Nada de domínio aqui: o layout vem pronto do servidor
// (apresentar/disposicao.py). Sem este arquivo a tela continua inteira — o SVG
// aparece ajustado à largura e a tabela equivalente tem a mesma informação.
(() => {
  "use strict";
  const MIN = 0.4;
  const MAX = 4;

  document.querySelectorAll("[data-pan-zoom]").forEach((janela) => {
    const svg = janela.querySelector("svg");
    if (!svg) return;

    const largura = Number(svg.dataset.largura);
    const altura = Number(svg.dataset.altura);
    let vista = { x: 0, y: 0, w: largura, h: altura };

    const aplicar = () => svg.setAttribute("viewBox", `${vista.x} ${vista.y} ${vista.w} ${vista.h}`);
    const escala = () => largura / vista.w;

    const ampliar = (fator, cx = vista.x + vista.w / 2, cy = vista.y + vista.h / 2) => {
      const nova = Math.min(MAX, Math.max(MIN, escala() * fator));
      const w = largura / nova;
      const h = altura / nova;
      vista = { x: cx - (cx - vista.x) * (w / vista.w), y: cy - (cy - vista.y) * (h / vista.h), w, h };
      aplicar();
    };

    janela.querySelectorAll("[data-zoom]").forEach((botao) => {
      botao.addEventListener("click", () => {
        const acao = botao.dataset.zoom;
        if (acao === "tudo") { vista = { x: 0, y: 0, w: largura, h: altura }; aplicar(); }
        else ampliar(acao === "mais" ? 1.3 : 1 / 1.3);
      });
    });

    svg.addEventListener("wheel", (ev) => {
      if (!ev.ctrlKey && !ev.metaKey) return; // rolagem da página continua sendo da página
      ev.preventDefault();
      const caixa = svg.getBoundingClientRect();
      const cx = vista.x + ((ev.clientX - caixa.left) / caixa.width) * vista.w;
      const cy = vista.y + ((ev.clientY - caixa.top) / caixa.height) * vista.h;
      ampliar(ev.deltaY < 0 ? 1.15 : 1 / 1.15, cx, cy);
    }, { passive: false });

    let arrastando = null;
    svg.addEventListener("pointerdown", (ev) => {
      if (ev.target.closest("a")) return; // clique em etapa é navegação, não arrasto
      arrastando = { x: ev.clientX, y: ev.clientY };
      svg.classList.add("arrastando");
      svg.setPointerCapture(ev.pointerId);
    });
    svg.addEventListener("pointermove", (ev) => {
      if (!arrastando) return;
      const caixa = svg.getBoundingClientRect();
      vista.x -= ((ev.clientX - arrastando.x) / caixa.width) * vista.w;
      vista.y -= ((ev.clientY - arrastando.y) / caixa.height) * vista.h;
      arrastando = { x: ev.clientX, y: ev.clientY };
      aplicar();
    });
    const soltar = () => { arrastando = null; svg.classList.remove("arrastando"); };
    svg.addEventListener("pointerup", soltar);
    svg.addEventListener("pointercancel", soltar);
  });
})();
