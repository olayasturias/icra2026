#!/usr/bin/env python3
import json

with open('data/platforms/batches/batch_005.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

all_classifications = {
    'pp:1871': ('sim', ['sim']), 'pp:1872': ('arm', ['arm']), 'pp:1873': ('car', ['car']),
    'pp:1875': ('arm', ['arm']), 'pp:1879': ('sim', ['sim']), 'pp:1884': ('multi', ['multi']),
    'pp:1886': ('sim', ['sim']), 'pp:1897': ('arm', ['arm']), 'pp:1899': ('multi', ['multi']),
    'pp:1901': ('ugv', ['ugv']), 'pp:1903': ('arm', ['arm']), 'pp:1905': ('arm', ['arm']),
    'pp:1915': ('hand', ['hand']), 'pp:1916': ('arm', ['arm']), 'pp:1920': ('ugv', ['ugv']),
    'pp:1923': ('car', ['car']), 'pp:1925': ('hand', ['hand']), 'pp:1926': ('ugv', ['ugv']),
    'pp:1927': ('ugv', ['ugv']), 'pp:1933': ('sim', ['sim']), 'pp:1934': ('multi', ['multi']),
    'pp:1937': ('hand', ['hand']), 'pp:1941': ('sim', ['sim']), 'pp:1942': ('hand', ['hand']),
    'pp:1946': ('arm', ['arm']), 'pp:1947': ('sim', ['sim']), 'pp:1950': ('arm', ['arm']),
    'pp:1957': ('ugv', ['ugv']), 'pp:1958': ('arm', ['arm']), 'pp:1963': ('arm', ['arm']),
    'pp:1965': ('ugv', ['ugv']), 'pp:1968': ('ugv', ['ugv']), 'pp:1980': ('marine', ['marine']),
    'pp:1981': ('soft', ['soft']), 'pp:1982': ('multi', ['multi']), 'pp:1983': ('uav', ['uav']),
    'pp:1991': ('multi', ['multi']), 'pp:1992': ('arm', ['arm']), 'pp:1993': ('medical', ['medical']),
    'pp:1994': ('multi', ['multi']), 'pp:1998': ('car', ['car']), 'pp:2001': ('sim', ['sim']),
    'pp:2008': ('sim', ['sim']), 'pp:2011': ('arm', ['arm']), 'pp:2015': ('soft', ['soft']),
    'pp:2017': ('sim', ['sim']), 'pp:2020': ('arm', ['arm']), 'pp:2023': ('sim', ['sim']),
    'pp:2027': ('arm', ['arm']), 'pp:2033': ('arm', ['arm']), 'pp:2035': ('uav', ['uav']),
    'pp:2036': ('arm', ['arm']), 'pp:2041': ('multi', ['multi']), 'pp:2042': ('sim', ['sim']),
    'pp:2048': ('ugv', ['ugv']), 'pp:2051': ('arm', ['arm']), 'pp:2058': ('wearable', ['wearable']),
    'pp:2060': ('medical', ['medical']), 'pp:2061': ('arm', ['arm']), 'pp:2062': ('arm', ['arm']),
    'pp:2063': ('marine', ['marine']), 'pp:2064': ('arm', ['arm']), 'pp:2067': ('sim', ['sim']),
    'pp:2068': ('car', ['car']), 'pp:2069': ('ugv', ['ugv']), 'pp:2070': ('arm', ['arm']),
    'pp:2071': ('sim', ['sim']), 'pp:2073': ('ugv', ['ugv']), 'pp:2075': ('uav', ['uav']),
    'pp:2076': ('wearable', ['wearable']), 'pp:2077': ('arm', ['arm']), 'pp:2078': ('hand', ['hand']),
    'pp:2081': ('car', ['car']), 'pp:2082': ('car', ['car']), 'pp:2084': ('car', ['car']),
    'pp:2087': ('arm', ['arm']), 'pp:2092': ('ugv', ['ugv']), 'pp:2097': ('uav', ['uav']),
    'pp:2098': ('sim', ['sim']), 'pp:2103': ('ugv', ['ugv']), 'pp:2105': ('hand', ['hand']),
    'pp:2106': ('arm', ['arm']), 'pp:2107': ('sim', ['sim']), 'pp:2109': ('ugv', ['ugv']),
    'pp:2111': ('multi', ['multi']), 'pp:2113': ('sim', ['sim']), 'pp:2114': ('uav', ['uav']),
    'pp:2115': ('hand', ['hand']), 'pp:2118': ('ugv', ['ugv']), 'pp:2119': ('sim', ['sim']),
    'pp:2120': ('arm', ['arm']), 'pp:2122': ('car', ['car']), 'pp:2123': ('arm', ['arm']),
    'pp:2124': ('sim', ['sim']), 'pp:2126': ('multi', ['multi']), 'pp:2127': ('sim', ['sim']),
    'pp:2128': ('sim', ['sim']), 'pp:2130': ('arm', ['arm']), 'pp:2131': ('arm', ['arm']),
    'pp:2132': ('ugv', ['ugv']), 'pp:2133': ('arm', ['arm']), 'pp:2134': ('legged', ['legged']),
    'pp:2137': ('sim', ['sim']), 'pp:2139': ('arm', ['arm']), 'pp:2140': ('legged', ['legged']),
    'pp:2141': ('micro', ['micro']), 'pp:2143': ('sim', ['sim']), 'pp:2144': ('arm', ['arm']),
    'pp:2145': ('marine', ['marine']), 'pp:2147': ('sim', ['sim']), 'pp:2149': ('arm', ['arm']),
    'pp:2150': ('sim', ['sim']), 'pp:2151': ('humanoid', ['humanoid']), 'pp:2152': ('arm', ['arm']),
    'pp:2153': ('multi', ['multi']), 'pp:2154': ('sim', ['sim']), 'pp:2157': ('uav', ['uav']),
    'pp:2158': ('legged', ['legged']), 'pp:2159': ('sim', ['sim']), 'pp:2161': ('humanoid', ['humanoid']),
    'pp:2162': ('mobile_manip', ['mobile_manip']), 'pp:2163': ('car', ['car']), 'pp:2165': ('arm', ['arm']),
    'pp:2166': ('sim', ['sim']), 'pp:2168': ('arm', ['arm']), 'pp:2169': ('arm', ['arm']),
    'pp:2170': ('ugv', ['ugv']), 'pp:2172': ('sim', ['sim']), 'pp:2173': ('arm', ['arm']),
    'pp:2174': ('sim', ['sim']), 'pp:2175': ('multi', ['multi']), 'pp:2176': ('legged', ['legged']),
    'pp:2177': ('arm', ['arm']), 'pp:2178': ('sim', ['sim']), 'pp:2179': ('humanoid', ['humanoid']),
    'pp:2180': ('arm', ['arm']), 'pp:2181': ('sim', ['sim']), 'pp:2182': ('legged', ['legged']),
    'pp:2183': ('arm', ['arm']), 'pp:2184': ('sim', ['sim']), 'pp:2185': ('sim', ['sim']),
    'pp:2186': ('arm', ['arm']), 'pp:2187': ('sim', ['sim']), 'pp:2188': ('legged', ['legged']),
    'pp:2190': ('arm', ['arm']), 'pp:2191': ('sim', ['sim']), 'pp:2192': ('arm', ['arm']),
    'pp:2193': ('legged', ['legged']), 'pp:2194': ('ugv', ['ugv']), 'pp:2195': ('sim', ['sim']),
    'pp:2196': ('arm', ['arm']), 'pp:2197': ('arm', ['arm']), 'pp:2198': ('car', ['car']),
    'pp:2200': ('sim', ['sim']), 'pp:2202': ('sim', ['sim']), 'pp:2203': ('arm', ['arm']),
    'pp:2204': ('sim', ['sim']), 'pp:2205': ('sim', ['sim']), 'pp:2206': ('arm', ['arm']),
    'pp:2207': ('sim', ['sim']), 'pp:2209': ('ugv', ['ugv']), 'pp:2210': ('sim', ['sim']),
    'pp:2212': ('multi', ['multi']), 'pp:2213': ('sim', ['sim']), 'pp:2214': ('arm', ['arm']),
    'pp:2215': ('arm', ['arm']), 'pp:2216': ('sim', ['sim']), 'pp:2217': ('arm', ['arm']),
    'pp:2218': ('uav', ['uav']), 'pp:2219': ('sim', ['sim']), 'pp:2220': ('hand', ['hand']),
    'pp:2222': ('arm', ['arm']), 'pp:2223': ('sim', ['sim']), 'pp:2224': ('car', ['car']),
    'pp:2225': ('sim', ['sim']), 'pp:2226': ('arm', ['arm']), 'pp:2227': ('sim', ['sim']),
    'pp:2229': ('arm', ['arm']), 'pp:2230': ('sim', ['sim']), 'pp:2231': ('sim', ['sim']),
    'pp:2232': ('multi', ['multi']), 'pp:2233': ('arm', ['arm']), 'pp:2234': ('sim', ['sim']),
    'pp:2235': ('arm', ['arm']), 'pp:2236': ('sim', ['sim']), 'pp:2237': ('sim', ['sim']),
    'pp:2238': ('arm', ['arm']), 'pp:2239': ('legged', ['legged']), 'pp:2240': ('sim', ['sim']),
    'pp:2241': ('sim', ['sim']), 'pp:2243': ('arm', ['arm']), 'pp:2244': ('sim', ['sim']),
    'pp:2245': ('sim', ['sim']), 'pp:2246': ('arm', ['arm']), 'pp:2247': ('sim', ['sim']),
    'pp:2248': ('arm', ['arm']), 'pp:2249': ('sim', ['sim']), 'pp:2250': ('sim', ['sim']),
    'pp:2251': ('sim', ['sim']), 'pp:2252': ('arm', ['arm']), 'pp:2253': ('arm', ['arm']),
    'pp:2254': ('sim', ['sim']), 'pp:2255': ('sim', ['sim']), 'pp:2256': ('arm', ['arm']),
    'pp:2257': ('arm', ['arm']), 'pp:2258': ('sim', ['sim']), 'pp:2259': ('arm', ['arm']),
    'pp:2260': ('car', ['car']), 'pp:2261': ('ugv', ['ugv']), 'pp:2262': ('sim', ['sim']),
    'pp:2264': ('sim', ['sim']), 'pp:2265': ('arm', ['arm']), 'pp:2267': ('arm', ['arm']),
    'pp:2270': ('sim', ['sim']), 'pp:2271': ('sim', ['sim']), 'pp:2272': ('sim', ['sim']),
    'pp:2273': ('sim', ['sim']), 'pp:2274': ('legged', ['legged']), 'pp:2275': ('arm', ['arm']),
    'pp:2276': ('sim', ['sim']), 'pp:2277': ('sim', ['sim']), 'pp:2279': ('sim', ['sim']),
    'pp:2280': ('arm', ['arm']), 'pp:2281': ('multi', ['multi']), 'pp:2282': ('sim', ['sim']),
    'pp:2283': ('sim', ['sim']), 'pp:2285': ('sim', ['sim']), 'pp:2286': ('arm', ['arm']),
    'pp:2287': ('sim', ['sim']), 'pp:2288': ('uav', ['uav']), 'pp:2289': ('sim', ['sim']),
    'pp:2290': ('sim', ['sim']), 'pp:2291': ('arm', ['arm']), 'pp:2292': ('sim', ['sim']),
    'pp:2293': ('sim', ['sim']), 'pp:2294': ('arm', ['arm']), 'pp:2295': ('ugv', ['ugv']),
    'pp:2296': ('sim', ['sim']), 'pp:2297': ('arm', ['arm']), 'pp:2298': ('sim', ['sim']),
    'pp:2299': ('arm', ['arm']), 'pp:2300': ('sim', ['sim']), 'pp:2301': ('arm', ['arm']),
    'pp:2302': ('sim', ['sim']), 'pp:2304': ('arm', ['arm']), 'pp:2305': ('sim', ['sim']),
    'pp:2306': ('arm', ['arm']), 'pp:2307': ('sim', ['sim']), 'pp:2308': ('sim', ['sim']),
    'pp:2309': ('arm', ['arm']), 'pp:2310': ('sim', ['sim']), 'pp:2311': ('arm', ['arm']),
    'pp:2312': ('sim', ['sim']), 'pp:2313': ('sim', ['sim']), 'pp:2314': ('arm', ['arm']),
    'pp:2315': ('sim', ['sim']), 'pp:2316': ('sim', ['sim']), 'pp:2317': ('arm', ['arm']),
    'pp:2318': ('sim', ['sim']), 'pp:2319': ('arm', ['arm']), 'pp:2320': ('sim', ['sim']),
    'pp:2322': ('arm', ['arm']),
}

classification = {pid: {'topics': topics, 'primary': primary}
                 for pid, (primary, topics) in all_classifications.items()}

assert len(classification) == len(papers), f"Count: {len(classification)} vs {len(papers)}"

platform_counts = {}
for data in classification.values():
    primary = data['primary']
    platform_counts[primary] = platform_counts.get(primary, 0) + 1

with open('data/platforms/out/batch_005.json', 'w', encoding='utf-8') as f:
    json.dump(classification, f, indent=2, ensure_ascii=False)

print(f"Classification complete: {len(classification)} papers")
print("\nPlatform distribution:")
for platform in sorted(platform_counts.keys()):
    pct = 100.0 * platform_counts[platform] / len(classification)
    print(f"  {platform}: {platform_counts[platform]:3d} ({pct:5.1f}%)")
print(f"\nOutput: data/platforms/out/batch_005.json")
