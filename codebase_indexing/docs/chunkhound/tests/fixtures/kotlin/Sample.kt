package com.example.chunkhound

import kotlinx.coroutines.*

/**
 * Sample Kotlin class for testing ChunkHound parsing
 */
data class User(
    val id: Long,
    val name: String,
    val email: String
) {
    fun getDisplayName(): String = "$name <$email>"
}

interface UserRepository {
    suspend fun findById(id: Long): User?
    suspend fun save(user: User): User
    suspend fun delete(id: Long): Boolean
}

class UserService(private val repository: UserRepository) {
    
    suspend fun createUser(name: String, email: String): User {
        val user = User(
            id = generateId(),
            name = name,
            email = email
        )
        return repository.save(user)
    }

    suspend fun getUser(id: Long): User? {
        return repository.findById(id)
    }

    private fun generateId(): Long = System.currentTimeMillis()

    companion object {
        const val MAX_NAME_LENGTH = 100
        
        fun validateEmail(email: String): Boolean {
            return email.contains("@") && email.contains(".")
        }
    }
}

object UserCache {
    private val cache = mutableMapOf<Long, User>()
    
    fun put(user: User) {
        cache[user.id] = user
    }
    
    fun get(id: Long): User? = cache[id]
    
    fun clear() = cache.clear()
}

enum class UserStatus {
    ACTIVE,
    INACTIVE,
    SUSPENDED,
    DELETED;
    
    fun isAvailable(): Boolean = this in listOf(ACTIVE, INACTIVE)
}

// Extension function
fun String.isValidEmail(): Boolean = UserService.validateEmail(this)

// Top-level function
fun formatUser(user: User): String {
    return "${user.name} (${user.id})"
}