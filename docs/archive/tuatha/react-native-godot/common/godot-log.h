/**************************************************************************/
/*  godot-log.h                                                           */
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

#pragma once

#ifndef LOG_TAG
#error "You should define LOG_TAG before including this header"
#endif

#ifdef ANDROID

#include <android/log.h>

#define LOGV(...) __android_log_print(ANDROID_LOG_VERBOSE, LOG_TAG, __VA_ARGS__)
#define LOGD(...) __android_log_print(ANDROID_LOG_DEBUG, LOG_TAG, __VA_ARGS__)
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGW(...) __android_log_print(ANDROID_LOG_WARN, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

#else

typedef enum ios_LogPriority {
	ANDROID_LOG_UNKNOWN = 0,
	IOS_LOG_DEFAULT, /* only for SetMinPriority() */
	IOS_LOG_VERBOSE,
	IOS_LOG_DEBUG,
	IOS_LOG_INFO,
	IOS_LOG_WARN,
	IOS_LOG_ERROR,
	IOS_LOG_FATAL,
	IOS_LOG_SILENT, /* only for SetMinPriority(); must be last */
} ios_LogPriority;

void __ios_log_print(ios_LogPriority prio, const char *tag, ...);

#define LOGV(...) __ios_log_print(IOS_LOG_VERBOSE, LOG_TAG, __VA_ARGS__)
#define LOGD(...) __ios_log_print(IOS_LOG_VERBOSE, LOG_TAG, __VA_ARGS__)
#define LOGI(...) __ios_log_print(IOS_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGW(...) __ios_log_print(IOS_LOG_WARN, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __ios_log_print(IOS_LOG_ERROR, LOG_TAG, __VA_ARGS__)

#endif
