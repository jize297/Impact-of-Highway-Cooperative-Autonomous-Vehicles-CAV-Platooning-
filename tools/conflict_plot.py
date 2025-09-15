import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt


net_file = 'M50network.net.xml'       
ssm_file = 'ssm_CAV2.xml'  


tree_net = ET.parse(net_file)
root_net = tree_net.getroot()

lane_shapes = []
for lane in root_net.findall('.//lane'):
    shape = lane.get('shape')
    if shape:
        pts = [tuple(map(float, coord.split(','))) for coord in shape.split()]
        lane_shapes.append(pts)


tree_ssm = ET.parse(ssm_file)
root_ssm = tree_ssm.getroot()

t_start, t_end = 25200, 27000
filtered_points = []
count_conflicts = 0

for c in root_ssm.findall('.//conflict'):
    begin = float(c.get('begin'))
    if t_start <= begin <= t_end:
 
        elem = c.find('minTTC')
        pos = elem.get('position')
        if pos and pos != 'NA':
            x, y = map(float, pos.split(','))
            filtered_points.append((x, y))
            count_conflicts += 1


plt.figure(figsize=(12, 8))

for pts in lane_shapes:
    xs, ys = zip(*pts)
    plt.plot(xs, ys, color='gray', linewidth=0.5)


if filtered_points:
    xs, ys = zip(*filtered_points)
    plt.scatter(xs, ys, c='red', marker='x', s=50, label=f'Conflicts ({count_conflicts})')

plt.axis('equal')
plt.title(f'CAV2 as ego car(10%cav): Conflict Points between {t_start}s and {t_end}s (Total={count_conflicts})')
plt.xlabel('X coordinate')
plt.ylabel('Y coordinate')
plt.legend()
plt.tight_layout()
plt.show()


print(f" {t_start} to {t_end} s， {count_conflicts} were detected and were plotted.")
