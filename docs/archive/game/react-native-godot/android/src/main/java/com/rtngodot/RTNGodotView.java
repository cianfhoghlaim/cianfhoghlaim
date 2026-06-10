/**************************************************************************/
/*  RTNGodotView.java                                                     */
/**************************************************************************/
/* Copyright (c) 2024-2025 Slay GmbH                                      */
/*                                                                        */
/* Permission is hereby granted, free of charge, to any person obtaining  */
/* a copy of this software and associated documentation files (the        */
/* "Software"), to deal in the Software without restriction, including    */
/* without limitation the rights to use, copy, modify, merge, publish,    */
/* distribute, sublicense, and/or sell copies of the Software, and to     */
/* permit persons to whom the Software is furnished to do so, subject to  */
/* the following conditions:                                              */
/*                                                                        */
/* The above copyright notice and this permission notice shall be         */
/* included in all copies or substantial portions of the Software.        */
/*                                                                        */
/* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,        */
/* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF     */
/* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. */
/* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY   */
/* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,   */
/* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE      */
/* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                 */
/**************************************************************************/

package com.rtngodot;

import org.godotengine.godot.input.GodotInputHandler;

import android.annotation.SuppressLint;
import android.content.Context;
import android.util.AttributeSet;
import android.util.Log;
import android.view.MotionEvent;
import android.view.SurfaceHolder;
import android.view.SurfaceView;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

public class RTNGodotView extends SurfaceView implements SurfaceHolder.Callback2 {
	private static final String TAG = "RTNGodotView";

	private String windowName = "";

	private GodotInputHandler mInputHandler;

	public RTNGodotView(Context context) {
		super(context);
		this.configureComponent();
	}

	public RTNGodotView(Context context, @Nullable AttributeSet attrs) {
		super(context, attrs);
		this.configureComponent();
	}

	public RTNGodotView(Context context, @Nullable AttributeSet attrs, int defStyleAttr) {
		super(context, attrs, defStyleAttr);
		this.configureComponent();
	}

	private void configureComponent() {
		mInputHandler = RTNLibGodot.getInstance().getInputHandler();
		setLayoutParams(new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
		getHolder().addCallback(this);
	}

	public void setWindowName(String newWindowName) {
		windowName = newWindowName;
	}

	public String getWindowName() {
		return windowName;
	}

	@Override
	public void surfaceRedrawNeeded(@NonNull SurfaceHolder surfaceHolder) {
		Log.i(TAG, String.format("surfaceRedrawNeeded: %s %s", windowName, surfaceHolder.getSurface().toString()));
	}

	@Override
	public void surfaceCreated(@NonNull SurfaceHolder surfaceHolder) {
		Log.i(TAG, String.format("surfaceCreated: %s %s", windowName, surfaceHolder.getSurface().toString()));
	}

	@Override
	public void surfaceChanged(@NonNull SurfaceHolder surfaceHolder, int format, int width, int height) {
		Log.i(TAG, String.format("surfaceChanged: %s %s %d %d %d", windowName, surfaceHolder.getSurface().toString(), format, width, height));
		RTNLibGodot.getInstance().updateWindow(windowName, getSurfaceControl(), surfaceHolder, format, width, height);
	}

	@Override
	public void surfaceDestroyed(@NonNull SurfaceHolder surfaceHolder) {
		Log.i(TAG, String.format("surfaceRemoved: %s %s", windowName, surfaceHolder.getSurface().toString()));
		RTNLibGodot.getInstance().removeWindow(windowName);
	}

	@SuppressLint("ClickableViewAccessibility")
	@Override
	public boolean onTouchEvent(MotionEvent event) {
		super.onTouchEvent(event);
		return mInputHandler.onTouchEvent(event);
	}

	@Override
	public boolean onGenericMotionEvent(MotionEvent event) {
		return mInputHandler.onGenericMotionEvent(event);
	}

	@Override
	public boolean onCapturedPointerEvent(MotionEvent event) {
		return mInputHandler.onGenericMotionEvent(event);
	}

	private boolean canCapturePointer() {
		return true;
	}

	@Override
	public void requestPointerCapture() {
		if (canCapturePointer()) {
			super.requestPointerCapture();
			mInputHandler.onPointerCaptureChange(true);
		}
	}

	@Override
	public void releasePointerCapture() {
		super.releasePointerCapture();
		mInputHandler.onPointerCaptureChange(false);
	}

	@Override
	public void onPointerCaptureChange(boolean hasCapture) {
		super.onPointerCaptureChange(hasCapture);
		mInputHandler.onPointerCaptureChange(hasCapture);
	}
}