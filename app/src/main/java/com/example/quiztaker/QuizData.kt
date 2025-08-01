package com.example.quiztaker

object QuizData {
    fun parseInput(input: String): List<PhrasePair> {
        return input.lines().mapNotNull { line ->
            val parts = line.split("---------------")
            if (parts.size == 2) {
                PhrasePair(parts[0].trim(), parts[1].trim())
            } else null
        }
    }
}
