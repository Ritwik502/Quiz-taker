package com.example.quiztaker

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import android.widget.TextView
import android.widget.Button

class ResultActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_result)

        val score = intent.getIntExtra("score", 0)
        val total = intent.getIntExtra("total", 1)
        val percent = (score * 100 / total)
        val result: TextView = findViewById(R.id.finalScoreTextView)
        result.text = "Score: $score / $total
($percent%)"

        findViewById<Button>(R.id.finishBtn).setOnClickListener {
            finishAffinity()
        }
    }
}
