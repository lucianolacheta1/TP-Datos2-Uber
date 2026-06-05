/* Genera docs/slides/presentacion.pptx — Defensa TP Uber (Datos 2, UADE).
 * Contenido: docs/presentacion.md §5 + plan-pptx-defensa.md + justificacion-der.md.
 * Correr:  NODE_PATH="$(npm root -g)" node docs/slides/build_deck.js
 */
const pptxgen = require("pptxgenjs");

// ---------- paleta ----------
const NAVY = "16224A", NAVY2 = "243463", BLUE = "2E5BB8", ORANGE = "F2701E";
const WHITE = "FFFFFF", BG = "F5F7FB", INK = "1F2433", MUTE = "6B7185", LINE = "D8DEEA";
const PG = "336791", MONGO = "12A14B", CASS = "0E7C86", NEO = "8E5BD0", REDIS = "D82C20";

const HDR = "Georgia", BODY = "Calibri";
const shadow = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 135, opacity: 0.16 });

const pres = new pptxgen();
pres.defineLayout({ name: "W", width: 13.333, height: 7.5 });
pres.layout = "W";
pres.author = "Equipo TP Uber";
pres.title = "TP Uber - Datos 2 (UADE)";
const W = 13.333, H = 7.5;

// ---------- helpers ----------
function footer(slide, n) {
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: H - 0.32, w: W, h: 0.32, fill: { color: NAVY } });
  slide.addText("TP Uber  ·  Datos 2 (UADE)  ·  Cátedra Mosquera Prada", {
    x: 0.5, y: H - 0.32, w: 9, h: 0.32, fontFace: BODY, fontSize: 9, color: "C7CEE0", valign: "middle", margin: 0,
  });
  slide.addText(String(n), {
    x: W - 1, y: H - 0.32, w: 0.5, h: 0.32, fontFace: BODY, fontSize: 9, color: "C7CEE0", align: "right", valign: "middle", margin: 0,
  });
}
function titleBar(slide, kicker, title) {
  slide.background = { color: BG };
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 1.25, fill: { color: NAVY } });
  slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 1.25, w: W, h: 0.06, fill: { color: ORANGE } });
  if (kicker) slide.addText(kicker.toUpperCase(), { x: 0.6, y: 0.18, w: 12, h: 0.3, fontFace: BODY, fontSize: 12, color: ORANGE, bold: true, charSpacing: 3, margin: 0 });
  slide.addText(title, { x: 0.6, y: 0.46, w: 12.1, h: 0.7, fontFace: HDR, fontSize: 28, color: WHITE, bold: true, valign: "middle", margin: 0 });
}
function chip(slide, x, y, w, h, color, label, sub) {
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: shadow() });
  slide.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.11, h, fill: { color } });
  slide.addText(label, { x: x + 0.28, y: y + 0.12, w: w - 0.4, h: 0.4, fontFace: BODY, fontSize: 15, bold: true, color: INK, margin: 0, valign: "middle" });
  if (sub) slide.addText(sub, { x: x + 0.28, y: y + 0.52, w: w - 0.4, h: h - 0.6, fontFace: BODY, fontSize: 11.5, color: MUTE, margin: 0, valign: "top" });
}

// ======================================================== Slide 1 — Portada
let s = pres.addSlide();
s.background = { color: NAVY };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.14, fill: { color: ORANGE } });
// motif: 5 puntos de las bases
const dots = [PG, MONGO, CASS, NEO, REDIS];
dots.forEach((c, i) => s.addShape(pres.shapes.OVAL, { x: 0.62 + i * 0.42, y: 1.5, w: 0.26, h: 0.26, fill: { color: c } }));
s.addText("TP UBER", { x: 0.6, y: 2.0, w: 12, h: 1.3, fontFace: HDR, fontSize: 72, bold: true, color: WHITE, margin: 0 });
s.addText("Sistema de datos multi-base para una plataforma de transporte", {
  x: 0.62, y: 3.35, w: 11.5, h: 0.6, fontFace: BODY, fontSize: 22, color: "CAD3EC", margin: 0,
});
s.addShape(pres.shapes.RECTANGLE, { x: 0.62, y: 4.25, w: 4.2, h: 0.04, fill: { color: ORANGE } });
s.addText([
  { text: "Datos 2 — UADE", options: { bold: true, color: WHITE, breakLine: true } },
  { text: "Cátedra: Prof. Mosquera Prada", options: { color: "CAD3EC", breakLine: true } },
  { text: "Integrantes: Luciano Lacheta · [integrante 2] · [integrante 3] · [integrante 4] · [integrante 5]", options: { color: "CAD3EC", breakLine: true } },
  { text: "Fecha de defensa: [completar]", options: { color: "8FA0C8" } },
], { x: 0.62, y: 4.5, w: 12, h: 1.8, fontFace: BODY, fontSize: 15, lineSpacingMultiple: 1.25, margin: 0 });

// ======================================================== Slide 2 — Contexto
s = pres.addSlide();
titleBar(s, "Contexto", "El requisito que define el TP");
s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.7, w: 7.4, h: 3.1, fill: { color: NAVY2 }, shadow: shadow() });
s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.7, w: 0.12, h: 3.1, fill: { color: ORANGE } });
s.addText('"No les voy a evaluar código… lo que sí me interesa ver es cómo interactúan las bases de datos entre sí."', {
  x: 1.0, y: 1.95, w: 6.7, h: 1.9, fontFace: HDR, italic: true, fontSize: 20, color: WHITE, valign: "middle", margin: 0,
});
s.addText("— Prof. Mosquera Prada (video de presentación del TP)", { x: 1.0, y: 4.0, w: 6.6, h: 0.5, fontFace: BODY, fontSize: 13, color: "9DB0DA", margin: 0 });
s.addText([
  { text: "Qué construimos", options: { bold: true, color: ORANGE, breakLine: true, fontSize: 15 } },
  { text: "Una app tipo Uber (consola con menú) sobre 5 bases de datos.", options: { color: INK, breakLine: true } },
  { text: "", options: { breakLine: true, fontSize: 6 } },
  { text: "El criterio clave", options: { bold: true, color: ORANGE, breakLine: true, fontSize: 15 } },
  { text: "Las bases deben interactuar y mantener consistencia. Que no lo hagan es motivo de desaprobar.", options: { color: INK } },
], { x: 8.3, y: 1.85, w: 4.4, h: 3.1, fontFace: BODY, fontSize: 14, lineSpacingMultiple: 1.15, valign: "top", margin: 0 });
s.addText("1 relacional + 4 NoSQL · Todo en la nube · Cada acción escribe en varias bases", {
  x: 0.6, y: 5.2, w: 12.1, h: 0.6, fontFace: BODY, fontSize: 15, bold: true, color: BLUE, align: "center", margin: 0,
});
footer(s, 2);

// ======================================================== Slide 3 — DER + cambios
s = pres.addSlide();
titleBar(s, "DER", "Modificaciones al DER y su justificación");
// placeholder imagen DER
s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: 1.7, w: 4.5, h: 4.0, fill: { color: "E9EDF5" }, line: { color: BLUE, width: 1.5, dashType: "dash" } });
s.addText("[ Imagen del DER original\n(Uber.pdf) ]", { x: 0.6, y: 1.7, w: 4.5, h: 4.0, fontFace: BODY, fontSize: 14, color: MUTE, align: "center", valign: "middle" });
s.addText("DER conceptual recibido — se respeta el modelo de negocio", { x: 0.6, y: 5.75, w: 4.5, h: 0.4, fontFace: BODY, fontSize: 10.5, italic: true, color: MUTE, align: "center", margin: 0 });
// tabla E1-E5
const der = [
  [{ text: "#", options: { fill: { color: NAVY }, color: WHITE, bold: true, align: "center" } },
   { text: "Cambio", options: { fill: { color: NAVY }, color: WHITE, bold: true } },
   { text: "Por qué", options: { fill: { color: NAVY }, color: WHITE, bold: true } }],
  ["E1", "Reseña: FKs polimórficas → 2 FKs + discriminador tipo", "Una FK no puede apuntar a Usuario o Conductor a la vez"],
  ["E2", "Conductor–Vehículo: 1..* → 0..*", "Un conductor puede registrarse antes de cargar su auto"],
  ["E3", "UNIQUE en email, nro_licencia y placa", "Evita cuentas/registros duplicados"],
  ["E4", "estado con dominio enumerado (CHECK)", "VARCHAR libre permitía cualquier string"],
  ["E5", "duracion_min marcado como derivado (/)", "Se calcula de ts_fin − ts_inicio (se guarda por performance)"],
];
s.addTable(der, {
  x: 5.4, y: 1.7, w: 7.3, colW: [0.55, 3.5, 3.25], rowH: [0.45, 0.78, 0.62, 0.55, 0.62, 0.78],
  fontFace: BODY, fontSize: 11.5, color: INK, valign: "middle",
  border: { type: "solid", pt: 0.75, color: LINE }, fill: { color: WHITE }, align: "left",
});
footer(s, 3);

// ======================================================== Slide 4 — Stack
s = pres.addSlide();
titleBar(s, "Stack", "Cinco bases, una por paradigma — todo cloud");
const stack = [
  [PG, "PostgreSQL", "Relacional", "Neon", "Catálogo de identidad (usuario, conductor, vehículo)"],
  [MONGO, "MongoDB", "Documental", "Atlas", "Datos operativos: viajes, pagos, reseñas"],
  [CASS, "Cassandra", "Columnar / time-series", "DataStax Astra", "Ubicaciones GPS + agregados por día"],
  [NEO, "Neo4j", "Grafo", "Aura", "Coincidencias pasajero-conductor + vehículos"],
  [REDIS, "Redis", "Key-value", "Redis Cloud", "Sesiones con TTL + cache + última posición"],
];
let yy = 1.62;
stack.forEach((r) => {
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: yy, w: 12.1, h: 0.92, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: yy, w: 0.13, h: 0.92, fill: { color: r[0] } });
  s.addShape(pres.shapes.OVAL, { x: 0.95, y: yy + 0.26, w: 0.4, h: 0.4, fill: { color: r[0] } });
  s.addText(r[1], { x: 1.55, y: yy, w: 2.6, h: 0.92, fontFace: BODY, fontSize: 17, bold: true, color: INK, valign: "middle", margin: 0 });
  s.addText(r[2], { x: 4.2, y: yy, w: 2.7, h: 0.92, fontFace: BODY, fontSize: 13, color: BLUE, bold: true, valign: "middle", margin: 0 });
  s.addText(r[3], { x: 6.9, y: yy, w: 2.0, h: 0.92, fontFace: BODY, fontSize: 13, color: MUTE, valign: "middle", margin: 0 });
  s.addText(r[4], { x: 8.95, y: yy, w: 3.65, h: 0.92, fontFace: BODY, fontSize: 12.5, color: INK, valign: "middle", margin: 0 });
  yy += 1.04;
});
s.addText("Screenshots de las 5 consolas cloud → slide de respaldo / demo en vivo", {
  x: 0.6, y: 6.9, w: 12.1, h: 0.3, fontFace: BODY, fontSize: 10.5, italic: true, color: MUTE, align: "center", margin: 0,
});
footer(s, 4);

// ======================================================== Slide 5 — Arquitectura
s = pres.addSlide();
titleBar(s, "Arquitectura", "Postgres mínimo + NoSQL operativas");
// Postgres box (identidad)
s.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 1.9, w: 3.3, h: 3.6, fill: { color: "EAF1F7" }, line: { color: PG, width: 2 }, shadow: shadow() });
s.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 1.9, w: 3.3, h: 0.55, fill: { color: PG } });
s.addText("PostgreSQL — Identidad", { x: 0.7, y: 1.9, w: 3.3, h: 0.55, fontFace: BODY, fontSize: 13, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
s.addText([
  { text: "Catálogo mínimo e inmutable:", options: { italic: true, color: MUTE, breakLine: true, fontSize: 12 } },
  { text: "usuario", options: { bullet: true, breakLine: true, color: INK } },
  { text: "conductor", options: { bullet: true, breakLine: true, color: INK } },
  { text: "vehiculo", options: { bullet: true, color: INK } },
], { x: 1.0, y: 2.65, w: 2.8, h: 2.6, fontFace: BODY, fontSize: 14, valign: "top", margin: 0, paraSpaceAfter: 6 });
// flecha
s.addShape(pres.shapes.LINE, { x: 4.05, y: 3.7, w: 0.75, h: 0, line: { color: ORANGE, width: 3, endArrowType: "triangle" } });
// NoSQL operativas (2x2)
const ops = [
  [MONGO, "MongoDB", "viajes · pagos · reseñas"],
  [CASS, "Cassandra", "GPS (time-series) + agregados"],
  [NEO, "Neo4j", "coincidencias + vehículos como nodos"],
  [REDIS, "Redis", "sesiones (TTL) · cache · última pos"],
];
const ox = 5.0, oy = 1.9, ow = 3.75, oh = 1.72, gx = 0.18, gy = 0.18;
ops.forEach((o, i) => {
  const x = ox + (i % 2) * (ow + gx), y = oy + Math.floor(i / 2) * (oh + gy);
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: ow, h: oh, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: ow, h: 0.1, fill: { color: o[0] } });
  s.addText(o[1], { x: x + 0.2, y: y + 0.22, w: ow - 0.4, h: 0.4, fontFace: BODY, fontSize: 15, bold: true, color: o[0], margin: 0 });
  s.addText(o[2], { x: x + 0.2, y: y + 0.72, w: ow - 0.4, h: 0.8, fontFace: BODY, fontSize: 12.5, color: INK, margin: 0 });
});
s.addText("Cada base hace lo que mejor sabe. Postgres no se fuerza a lo que las NoSQL resuelven mejor — ni al revés.", {
  x: 0.7, y: 5.75, w: 12, h: 0.5, fontFace: BODY, fontSize: 14, bold: true, color: NAVY, align: "center", margin: 0,
});
footer(s, 5);

// ======================================================== Slide 6 — Mapeo casos -> base
s = pres.addSlide();
titleBar(s, "Casos de uso", "Los 7 casos → cada uno luce una base");
const casos = [
  [{ text: "#", options: { fill: { color: NAVY }, color: WHITE, bold: true, align: "center" } },
   { text: "Caso de uso", options: { fill: { color: NAVY }, color: WHITE, bold: true } },
   { text: "Base que lo resuelve", options: { fill: { color: NAVY }, color: WHITE, bold: true } }],
  ["1", "Top 3 reseñadores", "MongoDB (aggregate) + cache Redis"],
  ["2", "Método de pago menos usado", "MongoDB (aggregate)"],
  ["3", "Conductores inactivos del último mes", "Cassandra + Postgres (join app-side)"],
  ["4", "Tiempo promedio de viajes", "Cassandra + cache Redis"],
  ["5", "Pasajero-conductor con más de 1 viaje", "Neo4j (grafo)"],
  ["6", "Toyota con patente terminada en 'D'", "Neo4j (grafo)"],
  ["7", "Reseñas con rating 5 o menor a 2", "MongoDB (find)"],
];
s.addTable(casos, {
  x: 0.6, y: 1.65, w: 8.4, colW: [0.6, 4.6, 3.2], rowH: 0.5,
  fontFace: BODY, fontSize: 13.5, color: INK, valign: "middle",
  border: { type: "solid", pt: 0.75, color: LINE }, fill: { color: WHITE },
});
// distribución
s.addShape(pres.shapes.RECTANGLE, { x: 9.25, y: 1.65, w: 3.45, h: 4.5, fill: { color: NAVY2 }, shadow: shadow() });
s.addText("Distribución", { x: 9.45, y: 1.85, w: 3.1, h: 0.4, fontFace: HDR, fontSize: 17, bold: true, color: WHITE, margin: 0 });
const dist = [[MONGO, "MongoDB", "3 casos"], [CASS, "Cassandra", "2 casos"], [NEO, "Neo4j", "2 casos"], [PG, "PostgreSQL", "soporte / identidad"], [REDIS, "Redis", "cache transversal"]];
let dy = 2.45;
dist.forEach((d) => {
  s.addShape(pres.shapes.OVAL, { x: 9.5, y: dy + 0.05, w: 0.28, h: 0.28, fill: { color: d[0] } });
  s.addText(d[1], { x: 9.95, y: dy - 0.02, w: 1.7, h: 0.4, fontFace: BODY, fontSize: 13.5, bold: true, color: WHITE, margin: 0, valign: "middle" });
  s.addText(d[2], { x: 11.0, y: dy - 0.02, w: 1.6, h: 0.4, fontFace: BODY, fontSize: 12, color: "CAD3EC", margin: 0, valign: "middle", align: "right" });
  dy += 0.72;
});
footer(s, 6);

// ======================================================== Slide 7 — Flujo finalizar viaje
s = pres.addSlide();
titleBar(s, "Interacción entre bases", "Una sola acción → 4 bases en simultáneo");
// acción central
s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 3.0, w: 3.1, h: 1.5, fill: { color: ORANGE }, rectRadius: 0.12, shadow: shadow() });
s.addText([
  { text: "Finalizar viaje", options: { bold: true, fontSize: 18, color: WHITE, breakLine: true } },
  { text: "(una acción del usuario)", options: { fontSize: 12, color: "FFE6D2" } },
], { x: 0.7, y: 3.0, w: 3.1, h: 1.5, fontFace: BODY, align: "center", valign: "middle", margin: 0 });
// 4 destinos
const proj = [
  [MONGO, "MongoDB", "viaje → FINALIZADO  (Source of Truth)"],
  [CASS, "Cassandra", "ultima_actividad + viajes_finalizados_por_dia"],
  [NEO, "Neo4j", "arista VIAJO_CON  +1"],
  [REDIS, "Redis", "invalida cache de \"tiempo promedio\""],
];
const px = 5.0, pw = 7.6, ph = 0.95, pgap = 0.28;
let py = 1.75;
proj.forEach((p) => {
  s.addShape(pres.shapes.LINE, { x: 3.8, y: 3.75, w: px - 3.8, h: (py + ph / 2) - 3.75, line: { color: p[0], width: 2.5, endArrowType: "triangle" } });
  s.addShape(pres.shapes.RECTANGLE, { x: px, y: py, w: pw, h: ph, fill: { color: WHITE }, line: { color: LINE, width: 1 }, shadow: shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x: px, y: py, w: 0.12, h: ph, fill: { color: p[0] } });
  s.addText(p[1], { x: px + 0.3, y: py + 0.1, w: 2.4, h: ph - 0.2, fontFace: BODY, fontSize: 15, bold: true, color: p[0], valign: "middle", margin: 0 });
  s.addText(p[2], { x: px + 2.7, y: py + 0.1, w: pw - 2.9, h: ph - 0.2, fontFace: BODY, fontSize: 12.5, color: INK, valign: "middle", margin: 0 });
  py += ph + pgap;
});
s.addText("Patrón write-through best-effort: el SOT primero (crítico); las proyecciones se intentan y, si fallan, van a un outbox + reconciliación.", {
  x: 0.7, y: 6.55, w: 12, h: 0.5, fontFace: BODY, fontSize: 12.5, italic: true, color: MUTE, align: "center", margin: 0,
});
footer(s, 7);

// ======================================================== Slide 8 — Cierre
s = pres.addSlide();
s.background = { color: NAVY };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: W, h: 0.14, fill: { color: ORANGE } });
s.addText("Lecciones aprendidas", { x: 0.7, y: 0.7, w: 12, h: 0.8, fontFace: HDR, fontSize: 34, bold: true, color: WHITE, margin: 0 });
s.addText([
  { text: "La diversidad de paradigmas deja que cada base resuelva lo que mejor sabe.", options: { bullet: true, breakLine: true } },
  { text: "Mantener consistencia sin transacciones distribuidas pide un patrón explícito (write-through + reconciliación).", options: { bullet: true, breakLine: true } },
  { text: "Postgres no debe forzarse a lo que las NoSQL hacen mejor — ni viceversa.", options: { bullet: true, breakLine: true } },
  { text: "La flexibilidad de Mongo resolvió naturalmente el polimorfismo de Reseña, ambiguo en SQL.", options: { bullet: true, breakLine: true } },
  { text: "El caso 5 (coincidencias) muestra cómo un problema 'feo' en SQL se vuelve trivial en un grafo.", options: { bullet: true } },
], { x: 0.9, y: 1.9, w: 11.5, h: 3.3, fontFace: BODY, fontSize: 17, color: "E6EBF7", paraSpaceAfter: 12, margin: 0 });
s.addShape(pres.shapes.RECTANGLE, { x: 0.9, y: 5.45, w: 4.0, h: 0.05, fill: { color: ORANGE } });
s.addText("Gracias. ¿Preguntas?", { x: 0.9, y: 5.7, w: 11, h: 0.9, fontFace: HDR, fontSize: 30, bold: true, color: WHITE, margin: 0 });

// ---------- write ----------
pres.writeFile({ fileName: "docs/slides/presentacion.pptx" }).then((f) => console.log("OK escrito:", f));
