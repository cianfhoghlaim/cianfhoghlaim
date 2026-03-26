// 统一的Fetch服务封装

export interface FetchOptions extends RequestInit {
  params?: Record<string, any>;
}

export interface ApiError {
  message: string;
  code?: string;
  status?: number;
}

class FetchService {
  private baseURL: string;

  constructor() {
    this.baseURL = "";
  }

  private buildURL(url: string, params?: Record<string, any>): string {
    const fullURL = url.startsWith("http") ? url : `${this.baseURL}${url}`;

    if (!params) return fullURL;

    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    });

    const queryString = searchParams.toString();
    return queryString ? `${fullURL}?${queryString}` : fullURL;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
       if (response.status === 401) {
      // 重定向登录
      window.location.href = '/login';
    } 

      let errorMessage = `HTTP error! status: ${response.status}`;

      try {
        const errorData = await response.json();
        errorMessage = errorData.message || errorData.error || errorMessage;
      } catch {
        // 如果无法解析JSON，使用默认错误消息
      }

      throw {
        message: errorMessage,
        status: response.status,
      } as ApiError;
    } 

    const contentType = response.headers.get("content-type");

    if (contentType?.includes("application/json")) {
      return await response.json();
    }

    return (await response.text()) as unknown as T;
  }

  async get<T>(url: string, options: FetchOptions = {}): Promise<T> {
    const { params, ...fetchOptions } = options;
    const fullURL = this.buildURL(url, params);

    const response = await fetch(fullURL, {
      ...fetchOptions,
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...fetchOptions.headers,
      },
    });

    return this.handleResponse<T>(response);
  }

  async post<T>(
    url: string,
    data?: any,
    options: FetchOptions = {}
  ): Promise<T> {
    const { params, ...fetchOptions } = options;
    const fullURL = this.buildURL(url, params);

    const response = await fetch(fullURL, {
      ...fetchOptions,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...fetchOptions.headers,
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    return this.handleResponse<T>(response);
  }

  async put<T>(
    url: string,
    data?: any,
    options: FetchOptions = {}
  ): Promise<T> {
    const { params, ...fetchOptions } = options;
    const fullURL = this.buildURL(url, params);

    const response = await fetch(fullURL, {
      ...fetchOptions,
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        ...fetchOptions.headers,
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    return this.handleResponse<T>(response);
  }

  async delete<T>(url: string, options: FetchOptions = {}): Promise<T> {
    const { params, ...fetchOptions } = options;
    const fullURL = this.buildURL(url, params);

    const response = await fetch(fullURL, {
      ...fetchOptions,
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        ...fetchOptions.headers,
      },
    });

    return this.handleResponse<T>(response);
  }
}

// 创建默认实例
export const fetchService = new FetchService();

// 导出类以便创建新实例
export default FetchService;
