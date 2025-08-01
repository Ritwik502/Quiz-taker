import os

# ----- Project structure -----
files = {
    # Gradle files
    "build.gradle": """
// Top-level build file
buildscript {
    ext.kotlin_version = '1.9.0'
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath "com.android.tools.build:gradle:8.1.0"
        classpath "org.jetbrains.kotlin:kotlin-gradle-plugin:$kotlin_version"
    }
}
allprojects {
    repositories {
        google()
        mavenCentral()
    }
}
task clean(type: Delete) {
    delete rootProject.buildDir
}
""",
    "settings.gradle": 'include \':app\'',
    "app/build.gradle": """
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}
android {
    compileSdk 34
    defaultConfig {
        applicationId "com.example.quiztaker"
        minSdk 21
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_11
        targetCompatibility JavaVersion.VERSION_11
    }
    kotlinOptions {
        jvmTarget = '11'
    }
    namespace 'com.example.quiztaker'
}
dependencies {
    implementation "org.jetbrains.kotlin:kotlin-stdlib:1.9.0"
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
}
""",
    "app/proguard-rules.pro": "",
    # Manifest
    "app/src/main/AndroidManifest.xml": """
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.quiztaker">
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="Quiz Taker"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.QuizTaker">
        <activity android:name=".ResultActivity"/>
        <activity android:name=".QuizActivity"/>
        <activity android:name=".MainActivity">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
""",
    # Kotlin Source Files
    "app/src/main/java/com/example/quiztaker/MainActivity.kt": """
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
""",
    "app/src/main/java/com/example/quiztaker/QuizActivity.kt": """
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
                resultText.text = "❌ Incorrect.\nCorrect: $correctAns"
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
""",
    "app/src/main/java/com/example/quiztaker/ResultActivity.kt": """
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
        result.text = "Score: $score / $total\n($percent%)"

        findViewById<Button>(R.id.finishBtn).setOnClickListener {
            finishAffinity()
        }
    }
}
""",
    "app/src/main/java/com/example/quiztaker/LevenshteinDistance.kt": """
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
""",
    "app/src/main/java/com/example/quiztaker/QuizData.kt": """
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
""",
    "app/src/main/java/com/example/quiztaker/PhrasePair.kt": """
package com.example.quiztaker

import android.os.Parcel
import android.os.Parcelable

data class PhrasePair(val hindi: String, val marathi: String) : Parcelable {
    constructor(parcel: Parcel) : this(
        parcel.readString() ?: "",
        parcel.readString() ?: ""
    )

    override fun writeToParcel(parcel: Parcel, flags: Int) {
        parcel.writeString(hindi)
        parcel.writeString(marathi)
    }

    override fun describeContents(): Int = 0

    companion object CREATOR : Parcelable.Creator<PhrasePair> {
        override fun createFromParcel(parcel: Parcel): PhrasePair = PhrasePair(parcel)
        override fun newArray(size: Int): Array<PhrasePair?> = arrayOfNulls(size)
    }
}
""",

    # XML Layouts
    "app/src/main/res/layout/activity_main.xml": """
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout 
  xmlns:android="http://schemas.android.com/apk/res/android"
  xmlns:app="http://schemas.android.com/apk/res-auto"
  android:layout_width="match_parent"
  android:layout_height="match_parent"
  android:padding="24dp">
    <EditText
        android:id="@+id/inputEditText"
        android:layout_width="0dp"
        android:layout_height="150dp"
        android:hint="Paste Hindi–Marathi phrase pairs here"
        android:gravity="top"
        android:inputType="textMultiLine"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintWidth_percent="1"
        android:scrollbars="vertical"
        android:background="@android:drawable/editbox_background"/>
    <Spinner
        android:id="@+id/directionSpinner"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        app:layout_constraintTop_toBottomOf="@id/inputEditText"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_margin="16dp" />
    <Button
        android:id="@+id/startQuizBtn"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:text="Start Quiz"
        app:layout_constraintTop_toBottomOf="@id/directionSpinner"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_margin="24dp"/>
</androidx.constraintlayout.widget.ConstraintLayout>
""",
    "app/src/main/res/layout/activity_quiz.xml": """
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout 
  xmlns:android="http://schemas.android.com/apk/res/android"
  xmlns:app="http://schemas.android.com/apk/res-auto"
  android:layout_width="match_parent"
  android:layout_height="match_parent"
  android:padding="24dp">
    <TextView
        android:id="@+id/progressTextView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Question 1 / 10"
        android:textStyle="bold"
        android:textSize="18sp"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintLeft_toLeftOf="parent"/>
    <TextView
        android:id="@+id/questionTextView"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:text="Question"
        android:textSize="24sp"
        android:textStyle="bold"
        app:layout_constraintTop_toBottomOf="@id/progressTextView"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_margin="32dp"/>
    <EditText
        android:id="@+id/answerEditText"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:hint="Type your answer…"
        app:layout_constraintTop_toBottomOf="@id/questionTextView"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_margin="24dp"/>
    <Button
        android:id="@+id/submitBtn"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:text="Submit"
        app:layout_constraintTop_toBottomOf="@id/answerEditText"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_margin="16dp"/>
    <TextView
        android:id="@+id/resultTextView"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:text=""
        android:textSize="18sp"
        android:textColor="#FF0000"
        android:gravity="center"
        app:layout_constraintTop_toBottomOf="@id/submitBtn"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_margin="16dp"/>
    <Button
        android:id="@+id/nextBtn"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:text="Next"
        android:enabled="false"
        app:layout_constraintTop_toBottomOf="@id/resultTextView"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_margin="16dp"/>
</androidx.constraintlayout.widget.ConstraintLayout>
""",
    "app/src/main/res/layout/activity_result.xml": """
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout 
  xmlns:android="http://schemas.android.com/apk/res/android"
  xmlns:app="http://schemas.android.com/apk/res-auto"
  android:layout_width="match_parent"
  android:layout_height="match_parent"
  android:padding="32dp">
    <TextView
        android:id="@+id/finalScoreTextView"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Score: 0 / 0"
        android:textStyle="bold"
        android:textSize="28sp"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_margin="48dp"
        android:gravity="center"/>
    <Button
        android:id="@+id/finishBtn"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:text="Finish"
        app:layout_constraintTop_toBottomOf="@id/finalScoreTextView"
        app:layout_constraintLeft_toLeftOf="parent"
        app:layout_constraintRight_toRightOf="parent"
        app:layout_constraintTop_margin="32dp"/>
</androidx.constraintlayout.widget.ConstraintLayout>
""",
    # Resource values
    "app/src/main/res/values/strings.xml": """
<resources>
    <string name="app_name">Quiz Taker</string>
</resources>
""",
    "app/src/main/res/values/colors.xml": """
<resources>
    <color name="purple_200">#BB86FC</color>
    <color name="purple_500">#6200EE</color>
    <color name="purple_700">#3700B3</color>
    <color name="teal_200">#03DAC5</color>
    <color name="teal_700">#018786</color>
    <color name="black">#000000</color>
    <color name="white">#FFFFFF</color>
</resources>
""",
    "app/src/main/res/values/themes.xml": """
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Theme.QuizTaker" parent="Theme.MaterialComponents.DayNight.NoActionBar">
        <item name="colorPrimary">@color/purple_500</item>
        <item name="colorPrimaryVariant">@color/purple_700</item>
        <item name="colorOnPrimary">@color/white</item>
        <item name="colorSecondary">@color/teal_200</item>
        <item name="colorSecondaryVariant">@color/teal_700</item>
        <item name="colorOnSecondary">@color/black</item>
        <item name="android:statusBarColor" tools:targetApi="l">@color/purple_700</item>
    </style>
</resources>
""",
}

# ----- File writing code -----
def create_project(files: dict):
    for path, content in files.items():
        # Correct for Windows/Unix paths
        filepath = os.path.normpath(path)
        folder = os.path.dirname(filepath)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
    print("All files have been created in the current directory.")

if __name__ == "__main__":
    create_project(files)
    