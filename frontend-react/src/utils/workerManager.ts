// Worker Manager for managing Web Workers

export interface WorkerMessage {
  type: string;
  data: any;
  id: string;
}

export interface WorkerResponse {
  type: "success" | "error" | "ready";
  data: any;
  id: string;
  workerId: string;
  timestamp: number;
}

export interface WorkerTask {
  id: string;
  type: string;
  data: any;
  resolve: (value: any) => void;
  reject: (error: any) => void;
  timestamp: number;
  timeout: number;
}

class WorkerManager {
  private workers: Worker[] = [];
  private maxWorkers: number;
  private tasks: Map<string, WorkerTask> = new Map();
  private availableWorkers: Worker[] = [];
  private busyWorkers: Set<Worker> = new Set();
  private taskQueue: WorkerTask[] = [];
  private isInitialized = false;

  constructor(maxWorkers = navigator.hardwareConcurrency || 4) {
    this.maxWorkers = maxWorkers;
  }

  async init() {
    if (this.isInitialized) return;

    console.log(`Initializing WorkerManager with ${this.maxWorkers} workers`);

    // Create workers
    for (let i = 0; i < this.maxWorkers; i++) {
      try {
        const worker = new Worker("/worker.js");
        this.setupWorker(worker);
        this.workers.push(worker);
        this.availableWorkers.push(worker);
      } catch (error) {
        console.warn(`Failed to create worker ${i}:`, error);
      }
    }

    this.isInitialized = true;
    console.log(
      `WorkerManager initialized with ${this.workers.length} workers`,
    );
  }

  private setupWorker(worker: Worker) {
    worker.addEventListener("message", (event) => {
      const response: WorkerResponse = event.data;

      if (response.type === "ready") {
        console.log(`Worker ${response.workerId} is ready`);
        return;
      }

      const task = this.tasks.get(response.id);
      if (!task) {
        console.warn(`Received response for unknown task: ${response.id}`);
        return;
      }

      // Remove task from tracking
      this.tasks.delete(response.id);

      // Mark worker as available
      this.busyWorkers.delete(worker);
      this.availableWorkers.push(worker);

      // Process response
      if (response.type === "success") {
        task.resolve(response.data);
      } else if (response.type === "error") {
        task.reject(new Error(response.data.message));
      }

      // Process next task in queue
      this.processNextTask();
    });

    worker.addEventListener("error", (error) => {
      console.error("Worker error:", error);
      // Handle worker error - could restart worker or mark as failed
    });
  }

  private processNextTask() {
    if (this.taskQueue.length === 0 || this.availableWorkers.length === 0) {
      return;
    }

    const task = this.taskQueue.shift()!;
    const worker = this.availableWorkers.shift()!;

    // Mark worker as busy
    this.busyWorkers.add(worker);

    // Send task to worker
    const message: WorkerMessage = {
      type: task.type,
      data: task.data,
      id: task.id,
    };

    worker.postMessage(message);

    // Set timeout
    setTimeout(() => {
      if (this.tasks.has(task.id)) {
        this.tasks.delete(task.id);
        task.reject(new Error("Task timeout"));

        // Mark worker as available
        this.busyWorkers.delete(worker);
        this.availableWorkers.push(worker);

        this.processNextTask();
      }
    }, task.timeout);
  }

  async executeTask(type: string, data: any, timeout = 30000): Promise<any> {
    if (!this.isInitialized) {
      await this.init();
    }

    return new Promise((resolve, reject) => {
      const taskId = `task-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

      const task: WorkerTask = {
        id: taskId,
        type,
        data,
        resolve,
        reject,
        timestamp: Date.now(),
        timeout,
      };

      this.tasks.set(taskId, task);

      if (this.availableWorkers.length > 0) {
        // Execute immediately
        this.processNextTask();
      } else {
        // Queue for later execution
        this.taskQueue.push(task);
      }
    });
  }

  // Convenience methods for common tasks
  async calculate(
    operation: string,
    numbers: number[],
    precision = 2,
  ): Promise<number> {
    return this.executeTask("calculate", { operation, numbers, precision });
  }

  async processData(dataset: any[], operations: any[]): Promise<any> {
    return this.executeTask("process_data", { dataset, operations });
  }

  async analyzeText(text: string): Promise<any> {
    return this.executeTask("analyze_text", { text });
  }

  async generateHash(text: string, algorithm = "sha256"): Promise<any> {
    return this.executeTask("generate_hash", { text, algorithm });
  }

  async compressData(text: string, algorithm = "simple"): Promise<any> {
    return this.executeTask("compress_data", { text, algorithm });
  }

  async validateData(schema: any, data: any): Promise<any> {
    return this.executeTask("validate_data", { schema, data });
  }

  // Batch processing
  async executeBatch(
    tasks: Array<{ type: string; data: any; timeout?: number }>,
  ): Promise<any[]> {
    const promises = tasks.map((task) =>
      this.executeTask(task.type, task.data, task.timeout),
    );
    return Promise.all(promises);
  }

  // Performance monitoring
  getStats() {
    return {
      totalWorkers: this.workers.length,
      availableWorkers: this.availableWorkers.length,
      busyWorkers: this.busyWorkers.size,
      queuedTasks: this.taskQueue.length,
      activeTasks: this.tasks.size,
      isInitialized: this.isInitialized,
    };
  }

  // Cleanup
  terminate() {
    console.log("Terminating WorkerManager");

    // Clear all tasks
    this.tasks.forEach((task) => {
      task.reject(new Error("WorkerManager terminated"));
    });
    this.tasks.clear();
    this.taskQueue = [];

    // Terminate all workers
    this.workers.forEach((worker) => {
      worker.terminate();
    });

    this.workers = [];
    this.availableWorkers = [];
    this.busyWorkers.clear();
    this.isInitialized = false;
  }
}

// Singleton instance
export const workerManager = new WorkerManager();

// Auto-initialize in development
if (process.env.NODE_ENV === "development") {
  workerManager.init();
}

export default workerManager;
