package com.example.quiztaker

object LevenshteinDistance {
    fun calculate(lhs: String, rhs: String): Int {
        val l = lhs.lowercase()
        val r = rhs.lowercase()
        val dp = Array(l.length + 1) { IntArray(r.length + 1) }
        for (i in 0..l.length)
            dp[i][0] = i
        for (j in 0..r.length)
            dp[0][j] = j
        for (i in 1..l.length) {
            for (j in 1..r.length) {
                val cost = if (l[i - 1] == r[j - 1]) 0 else 1
                dp[i][j] = minOf(
                    dp[i - 1][j] + 1,
                    dp[i][j - 1] + 1,
                    dp[i - 1][j - 1] + cost
                )
            }
        }
        return dp[l.length][r.length]
    }
}
