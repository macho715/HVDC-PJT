import { useEffect, useRef, useState } from 'react';
import { predictPressure } from '../utils/heat_stow_brain.js';
import * as d3 from 'd3';
export default function HeatStow() {
  const svgRef = useRef();
  const [data, setData] = useState([]);
  useEffect(() => {
    // demo grid 10x4
    const demo = Array.from({ length: 40 }, () => Math.random());
    setData(demo);
  }, []);
  useEffect(() => {
    if (!data.length) return;
    const pressures = predictPressure(data);
    const svg = d3.select(svgRef.current);
    const w = 400, h = 160;
    svg.attr('viewBox', `0 0 ${w} ${h}`);
    const color = d3.scaleSequential(d3.interpolateTurbo).domain([0, 1]);
    const cellW = w / 10, cellH = h / 4;
    svg.selectAll('rect').data(pressures).join('rect')
      .attr('x', (_, i) => (i % 10) * cellW)
      .attr('y', (_, i) => Math.floor(i / 10) * cellH)
      .attr('width', cellW - 1)
      .attr('height', cellH - 1)
      .attr('fill', d => color(d));
  }, [data]);
  return (<>
    <h1 className="text-2xl font-bold mb-4">Deck Heat‑Stow</h1>
    <svg ref={svgRef} className="border rounded-lg" />
  </>);
} 