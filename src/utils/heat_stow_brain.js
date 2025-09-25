import brain from 'brain.js';
const net = new brain.NeuralNetwork();
fetch('/model/heat_model.brain').then(r => r.json()).then(j => net.fromJSON(j));
export const predictPressure = (grid) => net.run(grid); 