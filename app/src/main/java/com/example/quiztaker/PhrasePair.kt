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
