from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, when


def main():
    # 1. 初始化 SparkSession（这里会自动读取集群集成的 OBS 配置）
    spark = SparkSession.builder \
        .appName("DoubanMovieCleaning") \
        .getOrCreate()

    # ==========================================================
    # 任务 1: 加载数据，打印 Schema 和前 5 行，统计缺失值比例
    # ==========================================================
    print("===== 1. 加载数据 =====")
    # 请根据课程群公告，将下面的路径修改为真实的 OBS 桶路径
    obs_path = "s3a://your-teacher-obs-bucket/douban_movies.csv"

    # 读取 CSV 文件
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(obs_path)

    # 打印 Schema 和前 5 行
    df.printSchema()
    df.show(5)

    # 记录清洗前的总行数
    total_count_before = df.count()
    print(f"清洗前总行数: {total_count_before}")

    # 统计各字段缺失值比例
    print("各字段缺失值比例:")
    df.select([
        (count(when(col(c).isNull() | (col(c) == "") | (col(c) == "NaN"), c)) / total_count_before).alias(c)
        for c in df.columns
    ]).show()

    # ==========================================================
    # 任务 2: 对至少 2 个有缺失值的字段采用不同处理策略
    # ==========================================================
    print("===== 2. 执行数据清洗策略 =====")

    # 策略一：对“片名 (title)”或“电影ID (movie_id)”字段采用 dropna
    # 选择原因：片名或ID是电影的核心标识，如果缺失则该条数据失去分析价值，故直接整行删除。
    df_cleaned = df.dropna(subset=["title"])

    # 策略二：对“评分 (rating)”或“年份 (year)”等数值/分类字段采用 fillna 填充
    # 选择原因：评分缺失可能是因为该电影小众无人评价，如果直接删除会丢失电影的其他属性（如类型、年份）。
    # 这里我们选择为缺失的评分填充默认值 0.0，或者填充平均分（例如 6.0）
    df_cleaned = df_cleaned.fillna({"rating": 0.0, "year": 1900})

    # ==========================================================
    # 任务 3: 输出清洗前后行数对比及各字段基本统计信息
    # ==========================================================
    print("===== 3. 清洗结果对比与统计 =====")
    # 统计清洗后的行数
    total_count_after = df_cleaned.count()
    print(f"清洗前后行数对比: 清洗前 = {total_count_before} 行, 清洗后 = {total_count_after} 行")

    # 输出清洗前各字段基本统计信息 (mean/std/min/max)
    print("清洗前数值字段统计信息:")
    df.describe().show()

    # 输出清洗后各字段基本统计信息
    print("清洗后数值字段统计信息:")
    df_cleaned.describe().show()

    # 关闭 Spark 绘画
    spark.stop()


if __name__ == "__main__":
    main()