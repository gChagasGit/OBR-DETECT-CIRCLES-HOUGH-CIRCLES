import xml.etree.ElementTree as ET
import cv2
import numpy as np
import os
import time
import argparse

# Parâmetros globais
WIDTH_IMAGE = 1160
HEIGHT_IMAGE = 872
HEIGHT_CUT = int(HEIGHT_IMAGE * 0.35)
THRESHOLD = 20

PATH_IMAGENS = '' #Preencha com o caminho onde se encontra as imagens
PATH_OUTPUT = '' #Preencha o caminho onde sero salvo o aarquivo TXT  

# Filtros
def blur(image):
    return cv2.medianBlur(image, 7)

def dilate(image, iterations=3):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    return cv2.dilate(image, kernel, iterations)

def sobel(image):
    sobelx = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)  # Derivada horizontal
    sobely = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)  # Derivada vertical
    gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
    return cv2.normalize(gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)

def edges(image):
    image_blur = cv2.GaussianBlur(image, (3, 3), 0)
    return cv2.Canny(image_blur, 35, 100)

# Função para extrair coordenadas do XML
def parse_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    annotations_esfera = {}
    annotations_esfera2 = {}

    for image in root.findall('image'):
        image_name = image.get('name')
        if image_name not in annotations_esfera:
            annotations_esfera[image_name] = []
            annotations_esfera2[image_name] = []
        
        for box in image.findall('box'):
            label_type = box.get('label')
            xtl = float(box.get('xtl'))
            ytl = float(box.get('ytl'))
            xbr = float(box.get('xbr'))
            ybr = float(box.get('ybr'))
            cx = (xtl + xbr) // 2
            cy = (ytl + ybr) // 2
            radius = ((xbr - xtl) / 2 + (ybr - ytl) / 2) // 2
            
            if label_type == 'esfera':
                annotations_esfera[image_name].append((cx, cy, radius))
                
            elif label_type == 'esfera2':
                annotations_esfera2[image_name].append((cx, cy, radius))
    return annotations_esfera, annotations_esfera2

# Função para detectar círculos usando HoughCircles
def detect_circles(image, dp=1.05, minDist=20, param1=75, param2=15, minRadius=15, maxRadius=165):
    circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, dp=dp,
                               minDist=minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        circles[:, 1] += HEIGHT_CUT
        return circles
    return []

# Função para comparar círculos anotados e detectados
def compare_circles(annotated, detected, img=None):
    matched = []
    radius_ratios = []
    
    for a in annotated:
        min_dist = np.inf
        closest_circle = None
        for d in detected:
            dist = np.sqrt((a[0] - d[0])**2 + (a[1] - d[1])**2)
            if dist < THRESHOLD:
                if dist < min_dist:
                    min_dist = dist
                    closest_circle = d

        if closest_circle is not None:
            matched.append((a, closest_circle))
            radius_ratios.append(closest_circle[2] / a[2])
            if img is not None:
                cv2.circle(img, (closest_circle[0], closest_circle[1]), closest_circle[2], (255, 0, 255), 5, 2)

    return matched, radius_ratios

# Função para processar uma imagem individual
def process_image(image_path, annotated_circles, filter_function, dp, minDist, param1, param2, minRadius, maxRadius):
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        print(f"Erro ao carregar a imagem em {image_path}")
        return 0, 0, 0, []

    image_resize = cv2.resize(image, (WIDTH_IMAGE, HEIGHT_IMAGE))
    image_cut = image_resize[HEIGHT_CUT:HEIGHT_IMAGE, :WIDTH_IMAGE]
    gray = cv2.cvtColor(image_cut, cv2.COLOR_BGR2GRAY)

    filtered_image = filter_function(gray)
    detected_circles = detect_circles(filtered_image, dp, minDist, param1, param2, minRadius, maxRadius)

    matched_circles, radius_ratios = compare_circles(annotated_circles, detected_circles, img=image_resize)
    num_annotated = len(annotated_circles)
    num_matched = len(matched_circles)

    return (num_matched / num_annotated if num_annotated != 0 else 0), num_matched, len(detected_circles), radius_ratios, num_annotated

# Função principal
def main():
    parser = argparse.ArgumentParser(description='Processamento de imagens e detecção de círculos.')
    parser.add_argument('output_file', type=str, help='Nome do arquivo de saída TXT para os resultados.')
    parser.add_argument('--dp', type=float, default=1.05, help='Parâmetro dp para HoughCircles.')
    parser.add_argument('--minDist', type=int, default=20, help='Parâmetro minDist para HoughCircles.')
    parser.add_argument('--param1', type=int, default=75, help='Parâmetro param1 para HoughCircles.')
    parser.add_argument('--param2', type=int, default=15, help='Parâmetro param2 para HoughCircles.')
    parser.add_argument('--minRadius', type=int, default=15, help='Parâmetro minRadius para HoughCircles.')
    parser.add_argument('--maxRadius', type=int, default=165, help='Parâmetro maxRadius para HoughCircles.')
    args = parser.parse_args()

    xml_file = './labels_doubles/annotations.xml'
    annotations_esfera, annotations_esfera2 = parse_xml(xml_file)

    filters = {'blur': blur, 'dilate': dilate, 'sobel': sobel, 'edges': edges}
    results = {key: {'esfera': [], 'esfera2': []} for key in filters.keys()}
    matcheds = {key: {'esfera': 0, 'esfera2': 0} for key in filters.keys()}
    detecteds = {key: {'esfera': 0, 'esfera2': 0} for key in filters.keys()}
    annotateds = {key: {'esfera': 0, 'esfera2': 0} for key in filters.keys()}
    all_radius_ratios = {key: {'esfera': [], 'esfera2': []} for key in filters.keys()}

    start = time.time()

    for filter_name, filter_function in filters.items():
        for image_name in annotations_esfera.keys():
            image_path = os.path.join(PATH_IMAGENS, image_name)
            if os.path.exists(image_path):
                if annotations_esfera[image_name]:
                    match_ratio_esfera, num_matched, num_detected, radius_ratios, num_annotated = process_image(image_path, annotations_esfera[image_name], filter_function,
                                                                                                 args.dp, args.minDist, args.param1, args.param2,
                                                                                                 args.minRadius, args.maxRadius)
                    results[filter_name]['esfera'].append((image_name, match_ratio_esfera))
                    matcheds[filter_name]['esfera'] += num_matched
                    detecteds[filter_name]['esfera'] += num_detected
                    all_radius_ratios[filter_name]['esfera'].extend(radius_ratios)
                    annotateds[filter_name]['esfera'] += num_annotated
                if annotations_esfera2[image_name]:
                    match_ratio_esfera2, num_matched2, num_detected2, radius_ratios2, num_annotated2 = process_image(image_path, annotations_esfera2[image_name], filter_function,
                                                                                                       args.dp, args.minDist, args.param1, args.param2,
                                                                                                       args.minRadius, args.maxRadius)
                    results[filter_name]['esfera2'].append((image_name, match_ratio_esfera2))
                    matcheds[filter_name]['esfera2'] += num_matched2
                    detecteds[filter_name]['esfera2'] += num_detected2
                    annotateds[filter_name]['esfera2'] += num_annotated2
                    all_radius_ratios[filter_name]['esfera2'].extend(radius_ratios2)

    end = time.time()

    with open(os.path.join(PATH_OUTPUT, args.output_file), 'w') as f:
        f.write(f"HC: {args.dp, args.minDist, args.param1, args.param2, args.minRadius, args.maxRadius}\n")
        for filter_name, filter_results in results.items():
            for sphere_type in ['esfera', 'esfera2']:
                size_filter_results = len(filter_results[sphere_type]) if len(filter_results[sphere_type]) > 0 else 1 
                size_all_radius_ratios = len(all_radius_ratios[filter_name][sphere_type]) if len(all_radius_ratios[filter_name][sphere_type]) > 0 else 1 
                f.write(f"Resultados para '{filter_name} - {sphere_type}':\n")
                f.write(f"    Media para '{sphere_type}': {((sum([result[1] for result in filter_results[sphere_type]]) / size_filter_results) * 100):.2f}%\n")
                f.write(f"    Media da relacao de raios para '{sphere_type}': {((sum(all_radius_ratios[filter_name][sphere_type]) / size_all_radius_ratios) * 100):.2f}%\n")
                f.write(f"    Detectados: {detecteds[filter_name][sphere_type]} | Matcheds: {matcheds[filter_name][sphere_type]} | Annotateds: {annotateds[filter_name][sphere_type]}\n\n")

        f.write(f"Tempo: {(end-start):.3f}s\n")

if __name__ == "__main__":
    main()
