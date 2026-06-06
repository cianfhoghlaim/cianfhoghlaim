namespace ImageAgent.Feishu;

public class FeiShuResult : FeiShuResultBase
{
    public object data { get; set; }
}

public class FeiShuResult<T> : FeiShuResultBase
{
    public T data { get; set; }
}

public class ImageUploadData
{
    public string image_key { get; set; }
}

public abstract class FeiShuResultBase
{
    public int code { get; set; }
    public string msg { get; set; }
}