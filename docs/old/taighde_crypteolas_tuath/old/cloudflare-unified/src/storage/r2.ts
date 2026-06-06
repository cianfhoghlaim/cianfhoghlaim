import type { R2Bucket } from "@cloudflare/workers-types";

/**
 * R2 File Storage Helper Functions
 *
 * Provides typed helpers for working with Cloudflare R2 object storage
 */

export interface UploadOptions {
  /**
   * Content type of the file
   */
  contentType?: string;
  /**
   * Custom metadata for the file
   */
  customMetadata?: Record<string, string>;
  /**
   * HTTP metadata
   */
  httpMetadata?: R2HTTPMetadata;
}

export interface R2HTTPMetadata {
  contentType?: string;
  contentLanguage?: string;
  contentDisposition?: string;
  contentEncoding?: string;
  cacheControl?: string;
}

export interface FileMetadata {
  key: string;
  size: number;
  uploaded: Date;
  contentType?: string;
  customMetadata?: Record<string, string>;
}

/**
 * Upload a file to R2
 */
export async function uploadFile(
  r2: R2Bucket,
  key: string,
  data: ReadableStream | ArrayBuffer | string,
  options?: UploadOptions
): Promise<void> {
  const r2Options: any = {};

  if (options?.contentType || options?.httpMetadata) {
    r2Options.httpMetadata = {
      contentType: options.contentType || options.httpMetadata?.contentType,
      ...options.httpMetadata,
    };
  }

  if (options?.customMetadata) {
    r2Options.customMetadata = options.customMetadata;
  }

  await r2.put(key, data, r2Options);
}

/**
 * Download a file from R2
 */
export async function downloadFile(
  r2: R2Bucket,
  key: string
): Promise<ReadableStream | null> {
  const object = await r2.get(key);
  return object?.body || null;
}

/**
 * Get file as ArrayBuffer
 */
export async function getFileAsArrayBuffer(
  r2: R2Bucket,
  key: string
): Promise<ArrayBuffer | null> {
  const object = await r2.get(key);
  return object ? await object.arrayBuffer() : null;
}

/**
 * Get file as text
 */
export async function getFileAsText(
  r2: R2Bucket,
  key: string
): Promise<string | null> {
  const object = await r2.get(key);
  return object ? await object.text() : null;
}

/**
 * Get file metadata
 */
export async function getFileMetadata(
  r2: R2Bucket,
  key: string
): Promise<FileMetadata | null> {
  const object = await r2.head(key);

  if (!object) {
    return null;
  }

  return {
    key,
    size: object.size,
    uploaded: object.uploaded,
    contentType: object.httpMetadata?.contentType,
    customMetadata: object.customMetadata,
  };
}

/**
 * Delete a file from R2
 */
export async function deleteFile(
  r2: R2Bucket,
  key: string
): Promise<void> {
  await r2.delete(key);
}

/**
 * Check if a file exists in R2
 */
export async function fileExists(
  r2: R2Bucket,
  key: string
): Promise<boolean> {
  const object = await r2.head(key);
  return object !== null;
}

/**
 * List files in R2 with optional prefix
 */
export async function listFiles(
  r2: R2Bucket,
  prefix?: string,
  limit?: number
): Promise<FileMetadata[]> {
  const listed = await r2.list({ prefix, limit });

  return listed.objects.map(obj => ({
    key: obj.key,
    size: obj.size,
    uploaded: obj.uploaded,
    contentType: obj.httpMetadata?.contentType,
    customMetadata: obj.customMetadata,
  }));
}

/**
 * Copy a file within R2
 */
export async function copyFile(
  r2: R2Bucket,
  sourceKey: string,
  destinationKey: string
): Promise<void> {
  const object = await r2.get(sourceKey);

  if (!object) {
    throw new Error(`Source file not found: ${sourceKey}`);
  }

  await r2.put(destinationKey, object.body, {
    httpMetadata: object.httpMetadata,
    customMetadata: object.customMetadata,
  });
}

/**
 * Generate a signed URL for temporary access (not available in R2, use presigned URLs via S3 API)
 */
export async function generatePublicUrl(
  bucketName: string,
  key: string
): Promise<string> {
  // R2 public URL format (if bucket has public access enabled)
  return `https://${bucketName}.r2.dev/${key}`;
}
