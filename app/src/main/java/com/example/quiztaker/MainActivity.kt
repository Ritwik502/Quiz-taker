package com.example.quiztaker

import android.content.Intent
import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val inputEditText: EditText = findViewById(R.id.inputEditText)
        val directionSpinner: Spinner = findViewById(R.id.directionSpinner)
        val startBtn: Button = findViewById(R.id.startQuizBtn)

        val directions = listOf("Hindi → Marathi", "Marathi → Hindi")
        directionSpinner.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, directions)

        startBtn.setOnClickListener {
            val input = inputEditText.text.toString()
            if (input.isBlank()) {
                Toast.makeText(this, "Please paste some phrase pairs.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val pairs = QuizData.parseInput(input)
            if (pairs.isEmpty()) {
                Toast.makeText(this, "Invalid input format.", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            val direction = directionSpinner.selectedItemPosition
            val intent = Intent(this, QuizActivity::class.java)
            intent.putParcelableArrayListExtra("phrasePairs", ArrayList(pairs))
            intent.putExtra("direction", direction)
            startActivity(intent)
        }
    }
}
