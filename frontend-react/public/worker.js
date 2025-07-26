// Web Worker for heavy computations and background tasks

// Message types
const MESSAGE_TYPES = {
  CALCULATE: "calculate",
  PROCESS_DATA: "process_data",
  ANALYZE_TEXT: "analyze_text",
  GENERATE_HASH: "generate_hash",
  COMPRESS_DATA: "compress_data",
  VALIDATE_DATA: "validate_data",
};

// Worker context
let workerId = null;

// Initialize worker
const initWorker = () => {
  workerId = `worker-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  console.log(`Worker ${workerId} initialized`);
};

// Send message to main thread
const sendMessage = (type, data, id) => {
  self.postMessage({
    type,
    data,
    id,
    workerId,
    timestamp: Date.now(),
  });
};

// Calculate function for heavy computations
const calculate = (data) => {
  const { operation, numbers, precision = 2 } = data;

  let result;

  switch (operation) {
    case "sum":
      result = numbers.reduce((acc, num) => acc + num, 0);
      break;
    case "average":
      result = numbers.reduce((acc, num) => acc + num, 0) / numbers.length;
      break;
    case "median": {
      const sorted = [...numbers].sort((a, b) => a - b);
      const mid = Math.floor(sorted.length / 2);
      result =
        sorted.length % 2 === 0
          ? (sorted[mid - 1] + sorted[mid]) / 2
          : sorted[mid];
      break;
    }
    case "standardDeviation": {
      const mean = numbers.reduce((acc, num) => acc + num, 0) / numbers.length;
      const variance =
        numbers.reduce((acc, num) => acc + Math.pow(num - mean, 2), 0) /
        numbers.length;
      result = Math.sqrt(variance);
      break;
    }
    case "factorial": {
      result = numbers.reduce((acc, num) => {
        let fact = 1;
        for (let i = 2; i <= num; i++) {
          fact *= i;
        }
        return acc + fact;
      }, 0);
      break;
    }
    case "fibonacci": {
      const fib = (n) => {
        if (n <= 1) return n;
        return fib(n - 1) + fib(n - 2);
      };
      result = numbers.map((num) => fib(num));
      break;
    }
    default:
      throw new Error(`Unknown operation: ${operation}`);
  }

  return Number(result.toFixed(precision));
};

// Process data function
const processData = (data) => {
  const { dataset, operations } = data;

  const results = {};

  operations.forEach((op) => {
    switch (op.type) {
      case "filter": {
        results[op.name] = dataset.filter((item) => {
          return op.conditions.every((condition) => {
            const value = item[condition.field];
            switch (condition.operator) {
              case "equals":
                return value === condition.value;
              case "not_equals":
                return value !== condition.value;
              case "greater_than":
                return value > condition.value;
              case "less_than":
                return value < condition.value;
              case "contains":
                return String(value).includes(condition.value);
              case "starts_with":
                return String(value).startsWith(condition.value);
              case "ends_with":
                return String(value).endsWith(condition.value);
              default:
                return true;
            }
          });
        });
        break;
      }

      case "sort": {
        results[op.name] = [...dataset].sort((a, b) => {
          const aVal = a[op.field];
          const bVal = b[op.field];
          return op.direction === "desc" ? bVal - aVal : aVal - bVal;
        });
        break;
      }

      case "group": {
        results[op.name] = dataset.reduce((groups, item) => {
          const key = item[op.field];
          if (!groups[key]) groups[key] = [];
          groups[key].push(item);
          return groups;
        }, {});
        break;
      }

      case "aggregate": {
        results[op.name] = dataset.reduce(
          (acc, item) => {
            const value = item[op.field];
            switch (op.operation) {
              case "sum":
                return acc + value;
              case "count":
                return acc + 1;
              case "average":
                return acc + value;
              case "min":
                return Math.min(acc, value);
              case "max":
                return Math.max(acc, value);
              default:
                return acc;
            }
          },
          op.operation === "min"
            ? Infinity
            : op.operation === "max"
              ? -Infinity
              : 0,
        );

        if (op.operation === "average") {
          results[op.name] = results[op.name] / dataset.length;
        }
        break;
      }
    }
  });

  return results;
};

// Analyze text function
const analyzeText = (data) => {
  const { text } = data;

  const analysis = {
    characterCount: text.length,
    wordCount: text.split(/\s+/).filter((word) => word.length > 0).length,
    sentenceCount: text
      .split(/[.!?]+/)
      .filter((sentence) => sentence.trim().length > 0).length,
    paragraphCount: text
      .split(/\n\s*\n/)
      .filter((para) => para.trim().length > 0).length,
    averageWordLength: 0,
    readingTime: 0,
    complexity: "medium",
    keywords: [],
    sentiment: "neutral",
  };

  // Calculate average word length
  const words = text.split(/\s+/).filter((word) => word.length > 0);
  if (words.length > 0) {
    const totalLength = words.reduce((acc, word) => acc + word.length, 0);
    analysis.averageWordLength = (totalLength / words.length).toFixed(2);
  }

  // Calculate reading time (average 200 words per minute)
  analysis.readingTime = Math.ceil(analysis.wordCount / 200);

  // Determine complexity based on average word length
  if (analysis.averageWordLength < 4) analysis.complexity = "easy";
  else if (analysis.averageWordLength > 6) analysis.complexity = "hard";

  // Extract keywords (simple implementation)
  const wordFreq = {};
  words.forEach((word) => {
    const cleanWord = word.toLowerCase().replace(/[^\w]/g, "");
    if (cleanWord.length > 3) {
      wordFreq[cleanWord] = (wordFreq[cleanWord] || 0) + 1;
    }
  });

  analysis.keywords = Object.entries(wordFreq)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10)
    .map(([word]) => word);

  // Simple sentiment analysis
  const positiveWords = [
    "good",
    "great",
    "excellent",
    "amazing",
    "wonderful",
    "love",
    "like",
    "happy",
  ];
  const negativeWords = [
    "bad",
    "terrible",
    "awful",
    "hate",
    "dislike",
    "sad",
    "angry",
    "frustrated",
  ];

  const positiveCount = positiveWords.filter((word) =>
    text.toLowerCase().includes(word),
  ).length;
  const negativeCount = negativeWords.filter((word) =>
    text.toLowerCase().includes(word),
  ).length;

  if (positiveCount > negativeCount) analysis.sentiment = "positive";
  else if (negativeCount > positiveCount) analysis.sentiment = "negative";

  return analysis;
};

// Generate hash function
const generateHash = (data) => {
  const { text, algorithm = "sha256" } = data;

  // Simple hash implementation (in real app, use crypto.subtle.digest)
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    const char = text.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash; // Convert to 32-bit integer
  }

  return {
    hash: Math.abs(hash).toString(16),
    algorithm,
    input: text,
    length: text.length,
  };
};

// Compress data function
const compressData = (data) => {
  const { text, algorithm = "simple" } = data;

  if (algorithm === "simple") {
    // Simple run-length encoding
    let compressed = "";
    let count = 1;
    let current = text[0];

    for (let i = 1; i < text.length; i++) {
      if (text[i] === current) {
        count++;
      } else {
        compressed += count + current;
        count = 1;
        current = text[i];
      }
    }
    compressed += count + current;

    return {
      original: text,
      compressed,
      compressionRatio: (compressed.length / text.length).toFixed(2),
      algorithm,
    };
  }

  return { error: "Unsupported compression algorithm" };
};

// Validate data function
const validateData = (data) => {
  const { schema, data: inputData } = data;

  const errors = [];
  const warnings = [];

  // Validate required fields
  schema.required?.forEach((field) => {
    if (!Object.prototype.hasOwnProperty.call(inputData, field)) {
      errors.push(`Missing required field: ${field}`);
    }
  });

  // Validate field types
  schema.fields?.forEach((field) => {
    const value = inputData[field.name];
    if (value !== undefined) {
      switch (field.type) {
        case "string":
          if (typeof value !== "string") {
            errors.push(`Field ${field.name} must be a string`);
          }
          if (field.minLength && value.length < field.minLength) {
            errors.push(
              `Field ${field.name} must be at least ${field.minLength} characters`,
            );
          }
          if (field.maxLength && value.length > field.maxLength) {
            errors.push(
              `Field ${field.name} must be at most ${field.maxLength} characters`,
            );
          }
          break;

        case "number": {
          if (typeof value !== "number" || isNaN(value)) {
            errors.push(`Field ${field.name} must be a number`);
          }
          if (field.min !== undefined && value < field.min) {
            errors.push(`Field ${field.name} must be at least ${field.min}`);
          }
          if (field.max !== undefined && value > field.max) {
            errors.push(`Field ${field.name} must be at most ${field.max}`);
          }
          break;
        }

        case "email":
          const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
          if (!emailRegex.test(value)) {
            errors.push(`Field ${field.name} must be a valid email address`);
          }
          break;

        case "url":
          try {
            new URL(value);
          } catch {
            errors.push(`Field ${field.name} must be a valid URL`);
          }
          break;
      }
    }
  });

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    data: inputData,
  };
};

// Message handler
self.addEventListener("message", (event) => {
  const { type, data, id } = event.data;

  try {
    let result;

    switch (type) {
      case MESSAGE_TYPES.CALCULATE:
        result = calculate(data);
        break;

      case MESSAGE_TYPES.PROCESS_DATA:
        result = processData(data);
        break;

      case MESSAGE_TYPES.ANALYZE_TEXT:
        result = analyzeText(data);
        break;

      case MESSAGE_TYPES.GENERATE_HASH:
        result = generateHash(data);
        break;

      case MESSAGE_TYPES.COMPRESS_DATA:
        result = compressData(data);
        break;

      case MESSAGE_TYPES.VALIDATE_DATA:
        result = validateData(data);
        break;

      default:
        throw new Error(`Unknown message type: ${type}`);
    }

    sendMessage("success", result, id);
  } catch (error) {
    sendMessage(
      "error",
      {
        message: error.message,
        stack: error.stack,
      },
      id,
    );
  }
});

// Initialize worker
initWorker();

// Send ready message
sendMessage("ready", { workerId }, null);
