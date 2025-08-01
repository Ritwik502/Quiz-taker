package com.example.quiztaker

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import android.widget.*
import kotlin.random.Random

class QuizActivity : AppCompatActivity() {
    private var phrasePairs: List<PhrasePair> = listOf()
    private var direction: Int = 0
    private var current: Int = 0
    private var score: Int = 0
    private var questionOrder: List<Int> = listOf()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_quiz)

        phrasePairs = intent.getParcelableArrayListExtra<PhrasePair>("phrasePairs") ?: listOf()
        direction = intent.getIntExtra("direction", 0)

        // Random order
        questionOrder = phrasePairs.indices.shuffled(Random(System.currentTimeMillis()))
        setQuestion()

        val submitBtn: Button = findViewById(R.id.submitBtn)
        val answerEditText: EditText = findViewById(R.id.answerEditText)
        submitBtn.setOnClickListener {
            val answer = answerEditText.text.toString().trim()
            val qIdx = questionOrder[current]
            val correct = if (direction == 0) phrasePairs[qIdx].marathi else phrasePairs[qIdx].hindi
            val correctAns = correct.trim()
            val distance = LevenshteinDistance.calculate(answer, correctAns)
            val correctEnough = distance <= 2
            val resultText: TextView = findViewById(R.id.resultTextView)
            if (correctEnough) {
                score++
                resultText.text = "✔️ Correct!"
            } else {
                resultText.text = "❌ Incorrect.
Correct: $correctAns"
            }
            answerEditText.setText("")
            submitBtn.isEnabled = false
            answerEditText.isEnabled = false
            val nextBtn: Button = findViewById(R.id.nextBtn)
            nextBtn.isEnabled = true
            nextBtn.setOnClickListener {
                current++
                if (current >= phrasePairs.size) {
                    val intent = Intent(this, ResultActivity::class.java)
                    intent.putExtra("score", score)
                    intent.putExtra("total", phrasePairs.size)
                    startActivity(intent)
                    finish()
                } else {
                    setQuestion()
                    resultText.text = ""
                    submitBtn.isEnabled = true
                    answerEditText.isEnabled = true
                    nextBtn.isEnabled = false
                }
            }
        }
    }

    private fun setQuestion() {
        val questionText: TextView = findViewById(R.id.questionTextView)
        val answerEditText: EditText = findViewById(R.id.answerEditText)
        answerEditText.setText("")
        val idx = questionOrder[current]
        questionText.text = if (direction == 0)
            phrasePairs[idx].hindi
        else
            phrasePairs[idx].marathi
        val progress: TextView = findViewById(R.id.progressTextView)
        progress.text = "Question ${current + 1} / ${phrasePairs.size}"
        findViewById<Button>(R.id.nextBtn).isEnabled = false
    }
}
