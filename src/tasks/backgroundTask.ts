import * as TaskManager from 'expo-task-manager'
import * as BackgroundTask from 'expo-background-task'
import { processQueueOnce } from '../services/queueService'

const TASK_NAME = 'PRODFLOW_QUEUE_TASK'

TaskManager.defineTask(TASK_NAME, async () => {
  try {
    await processQueueOnce()
    return BackgroundTask.BackgroundTaskResult.Success
  } catch (e) {
    return BackgroundTask.BackgroundTaskResult.Failed
  }
})

export async function registerBackgroundTask() {
  const isRegistered = await TaskManager.isTaskRegisteredAsync(TASK_NAME)
  if (!isRegistered) {
    await BackgroundTask.registerTaskAsync(TASK_NAME, {
      minimumInterval: 1
    })
  }
}
