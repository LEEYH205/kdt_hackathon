import pandas as pd
import numpy as np

def get_cluster_name(cluster_id, df):
    """클러스터 ID를 기반으로 의미있는 이름을 생성"""
    if cluster_id == -1:
        return '노이즈'
    
    cluster_data = df[df['cluster'] == cluster_id]
    
    # 주요 업종 대분류
    major_business = cluster_data['상권업종대분류명'].value_counts().index[0]
    
    # 주요 업종 중분류 (상위 2개)
    major_sub_business = cluster_data['상권업종중분류명'].value_counts().head(2)
    
    # 클러스터 크기
    cluster_size = len(cluster_data)
    
    # 이름 생성 규칙
    if major_business == '소매':
        if '식료품' in major_sub_business.index[0]:
            return f'식료품소매 ({cluster_size}개)'
        elif '의류' in major_sub_business.index[0]:
            return f'의류소매 ({cluster_size}개)'
        else:
            return f'소매업 ({cluster_size}개)'
    elif major_business == '음식':
        if '한식' in major_sub_business.index[0]:
            return f'한식점 ({cluster_size}개)'
        elif '카페' in major_sub_business.index[0]:
            return f'카페 ({cluster_size}개)'
        else:
            return f'음식점 ({cluster_size}개)'
    elif major_business == '수리·개인':
        if '이용·미용' in major_sub_business.index[0]:
            return f'미용업 ({cluster_size}개)'
        else:
            return f'수리서비스 ({cluster_size}개)'
    elif major_business == '부동산':
        return f'부동산 ({cluster_size}개)'
    elif major_business == '교육':
        return f'교육업 ({cluster_size}개)'
    elif major_business == '보건의료':
        return f'의료업 ({cluster_size}개)'
    elif major_business == '숙박':
        return f'숙박업 ({cluster_size}개)'
    elif major_business == '과학·기술':
        return f'기술서비스 ({cluster_size}개)'
    elif major_business == '시설관리·임대':
        return f'시설관리 ({cluster_size}개)'
    elif major_business == '예술·스포츠':
        return f'문화스포츠 ({cluster_size}개)'
    else:
        return f'{major_business} ({cluster_size}개)'

def print_cluster_info(df, cityname):
    """클러스터별 상세 정보를 출력"""
    print(f"\n=== {cityname} 클러스터별 상세 정보 ===")
    unique_clusters = np.unique(df['cluster'])

    for cluster_id in sorted(unique_clusters):
        if cluster_id != -1:
            cluster_data = df[df['cluster'] == cluster_id]
            cluster_name = get_cluster_name(cluster_id, df)
            
            print(f"\n{cluster_name}:")
            
            # 주요 업종
            major_business = cluster_data['상권업종대분류명'].value_counts().head(3)
            print(f"  주요 업종: {dict(major_business)}")
            
            # 주요 중분류
            major_sub = cluster_data['상권업종중분류명'].value_counts().head(3)
            print(f"  주요 중분류: {dict(major_sub)}")
            
            # 주요 지역
            major_area = cluster_data['행정동명'].value_counts().head(3)
            print(f"  주요 지역: {dict(major_area)}")
            
            # 샘플 상가
            sample_business = cluster_data['상권업종소분류명'].value_counts().head(3)
            print(f"  대표 업종: {dict(sample_business)}")
        else:
            print(f"\n노이즈 ({len(df[df['cluster'] == -1])}개):")
            noise_data = df[df['cluster'] == -1]
            print(f"  주요 업종: {dict(noise_data['상권업종대분류명'].value_counts().head(3))}")

def create_cluster_mapping(df):
    """클러스터 이름 매핑 딕셔너리 생성"""
    unique_clusters = np.unique(df['cluster'])
    cluster_name_mapping = {}
    
    for cluster_id in unique_clusters:
        cluster_name_mapping[cluster_id] = get_cluster_name(cluster_id, df)
    
    return cluster_name_mapping

def print_cluster_mapping(cluster_name_mapping):
    """클러스터 이름 매핑 출력"""
    print(f"\n=== 클러스터 이름 매핑 ===")
    for cluster_id, name in cluster_name_mapping.items():
        print(f"클러스터 {cluster_id} → {name}")

# 사용 예시
if __name__ == "__main__":
    # df와 cityname이 정의되어 있다고 가정
    # print_cluster_info(df, cityname)
    # cluster_mapping = create_cluster_mapping(df)
    # print_cluster_mapping(cluster_mapping)
    pass 