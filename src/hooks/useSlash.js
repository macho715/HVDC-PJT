import { useState, useEffect } from 'react';

export function useSlash() {
  const [commands, setCommands] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const executeCommand = async (cmd) => {
    setIsProcessing(true);
    try {
      let response;
      
      if (cmd.startsWith('/logi-master')) {
        response = await fetch(`/api/logi-master?${new URLSearchParams({ command: cmd })}`);
      } else if (cmd.startsWith('/ocr')) {
        response = await fetch(`/api/ocr?${new URLSearchParams({ command: cmd })}`);
      } else if (cmd.startsWith('/heat-stow')) {
        response = await fetch(`/api/heat-stow?${new URLSearchParams({ command: cmd })}`);
      } else if (cmd.startsWith('/forecast')) {
        response = await fetch(`/api/forecast?${new URLSearchParams({ command: cmd })}`);
      } else {
        throw new Error(`Unknown command: ${cmd}`);
      }
      
      const result = await response.json();
      setCommands(prev => [...prev, { cmd, result, timestamp: new Date() }]);
      return result;
    } catch (error) {
      console.error('Command execution failed:', error);
      setCommands(prev => [...prev, { cmd, error: error.message, timestamp: new Date() }]);
    } finally {
      setIsProcessing(false);
    }
  };

  return { commands, isProcessing, executeCommand };
} 