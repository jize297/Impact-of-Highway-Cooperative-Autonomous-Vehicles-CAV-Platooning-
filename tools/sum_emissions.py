import os
import xml.etree.ElementTree as ET


def stream_sum_by_eclass(file_path):
    """
    Stream-parse the large SUMO emission XML file and sum numeric attributes for each <vehicle>,
    grouped by their 'eclass'. Uses iterparse to avoid loading entire file into memory.
    """
    totals_by_eclass = {}
    # Use iterparse to process 'vehicle' elements as they end
    context = ET.iterparse(file_path, events=('end',))
    for event, elem in context:
        if elem.tag == 'vehicle':
            eclass = elem.attrib.get('eclass', 'Unknown')
            if eclass not in totals_by_eclass:
                totals_by_eclass[eclass] = {}
            for attr, value in elem.attrib.items():
                try:
                    val = float(value)
                except ValueError:
                    continue
                totals_by_eclass[eclass][attr] = totals_by_eclass[eclass].get(attr, 0.0) + val
            # Clear element to free memory
            elem.clear()
    return totals_by_eclass


if __name__ == '__main__':
    # Assume emission.xml is in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'emission.xml')

    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        exit(1)

    print("Streaming and summing emissions by eclass (this may take a while)...")
    grouped_totals = stream_sum_by_eclass(file_path)

    print("Done. Total sums per eclass category:")
    for eclass, totals in sorted(grouped_totals.items()):
        print(f"\n=== {eclass} ===")
        for metric, total in sorted(totals.items()):
            print(f"{metric}: {total}")
