// IndexedDB Service for Chat History Storage
import { ChatSession, ChatMessage } from '@/types/chat.types'

const DB_NAME = 'OpenDeepWikiChat'
const DB_VERSION = 1
const SESSIONS_STORE = 'sessions'

class ChatStorageService {
  private db: IDBDatabase | null = null
  private initPromise: Promise<void> | null = null

  /**
   * Initialize IndexedDB
   */
  async init(): Promise<void> {
    // Return existing DB if already initialized
    if (this.db) {
      return Promise.resolve()
    }

    // Return existing initialization promise if in progress
    if (this.initPromise) {
      return this.initPromise
    }

    // Start new initialization
    this.initPromise = new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      request.onerror = () => {
        this.initPromise = null
        reject(new Error('Failed to open IndexedDB'))
      }

      request.onsuccess = () => {
        this.db = request.result
        resolve()
      }

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result

        // Create sessions store if it doesn't exist
        if (!db.objectStoreNames.contains(SESSIONS_STORE)) {
          const objectStore = db.createObjectStore(SESSIONS_STORE, { keyPath: 'id' })

          // Create indexes
          objectStore.createIndex('organizationName', 'organizationName', { unique: false })
          objectStore.createIndex('repositoryName', 'repositoryName', { unique: false })
          objectStore.createIndex('appId', 'appId', { unique: false })
          objectStore.createIndex('updatedAt', 'updatedAt', { unique: false })
        }
      }
    })

    return this.initPromise
  }

  /**
   * Ensure DB is initialized
   */
  private async ensureDB(): Promise<IDBDatabase> {
    if (!this.db) {
      await this.init()
    }
    if (!this.db) {
      throw new Error('Database not initialized')
    }
    return this.db
  }

  /**
   * Generate session ID based on context
   */
  generateSessionId(organizationName?: string, repositoryName?: string, appId?: string): string {
    if (appId) {
      return `app-${appId}`
    }
    if (organizationName && repositoryName) {
      return `repo-${organizationName}-${repositoryName}`
    }
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * Save or update a chat session
   */
  async saveSession(session: ChatSession): Promise<void> {
    const db = await this.ensureDB()

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([SESSIONS_STORE], 'readwrite')
      const store = transaction.objectStore(SESSIONS_STORE)

      const request = store.put({
        ...session,
        updatedAt: Date.now()
      })

      request.onsuccess = () => resolve()
      request.onerror = () => reject(new Error('Failed to save session'))
    })
  }

  /**
   * Get a chat session by ID
   */
  async getSession(sessionId: string): Promise<ChatSession | null> {
    const db = await this.ensureDB()

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([SESSIONS_STORE], 'readonly')
      const store = transaction.objectStore(SESSIONS_STORE)
      const request = store.get(sessionId)

      request.onsuccess = () => {
        resolve(request.result || null)
      }
      request.onerror = () => reject(new Error('Failed to get session'))
    })
  }

  /**
   * Get session by repository
   */
  async getSessionByRepository(organizationName: string, repositoryName: string): Promise<ChatSession | null> {
    const sessionId = this.generateSessionId(organizationName, repositoryName)
    return this.getSession(sessionId)
  }

  /**
   * Get session by appId
   */
  async getSessionByAppId(appId: string): Promise<ChatSession | null> {
    const sessionId = this.generateSessionId(undefined, undefined, appId)
    return this.getSession(sessionId)
  }

  /**
   * Get all sessions
   */
  async getAllSessions(): Promise<ChatSession[]> {
    const db = await this.ensureDB()

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([SESSIONS_STORE], 'readonly')
      const store = transaction.objectStore(SESSIONS_STORE)
      const request = store.getAll()

      request.onsuccess = () => {
        const sessions = request.result || []
        // Sort by updatedAt descending
        sessions.sort((a, b) => b.updatedAt - a.updatedAt)
        resolve(sessions)
      }
      request.onerror = () => reject(new Error('Failed to get all sessions'))
    })
  }

  /**
   * Delete a session
   */
  async deleteSession(sessionId: string): Promise<void> {
    const db = await this.ensureDB()

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([SESSIONS_STORE], 'readwrite')
      const store = transaction.objectStore(SESSIONS_STORE)
      const request = store.delete(sessionId)

      request.onsuccess = () => resolve()
      request.onerror = () => reject(new Error('Failed to delete session'))
    })
  }

  /**
   * Clear all sessions
   */
  async clearAllSessions(): Promise<void> {
    const db = await this.ensureDB()

    return new Promise((resolve, reject) => {
      const transaction = db.transaction([SESSIONS_STORE], 'readwrite')
      const store = transaction.objectStore(SESSIONS_STORE)
      const request = store.clear()

      request.onsuccess = () => resolve()
      request.onerror = () => reject(new Error('Failed to clear sessions'))
    })
  }

  /**
   * Add message to session
   */
  async addMessage(sessionId: string, message: ChatMessage): Promise<void> {
    const session = await this.getSession(sessionId)

    if (!session) {
      throw new Error('Session not found')
    }

    session.messages.push(message)
    session.updatedAt = Date.now()

    await this.saveSession(session)
  }

  /**
   * Create new session
   */
  async createSession(
    organizationName?: string,
    repositoryName?: string,
    appId?: string
  ): Promise<ChatSession> {
    const sessionId = this.generateSessionId(organizationName, repositoryName, appId)

    const session: ChatSession = {
      id: sessionId,
      organizationName,
      repositoryName,
      appId,
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now()
    }

    await this.saveSession(session)
    return session
  }

  /**
   * Get or create session
   */
  async getOrCreateSession(
    organizationName?: string,
    repositoryName?: string,
    appId?: string
  ): Promise<ChatSession> {
    const sessionId = this.generateSessionId(organizationName, repositoryName, appId)
    let session = await this.getSession(sessionId)

    if (!session) {
      session = await this.createSession(organizationName, repositoryName, appId)
    }

    return session
  }
}

// Create singleton instance
export const chatStorageService = new ChatStorageService()

// Export class for testing
export default ChatStorageService
