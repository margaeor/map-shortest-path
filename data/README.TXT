#	$Id: README.TXT,v 1.6 2009/07/14 22:57:38 guru Exp $

Global Self-consistent Hierarchical High-resolution Shorelines
		version 2.0 July 15, 2009
		
	Distributed under the Gnu Public License
		
This is the README file for the GSHHS Data distribution.  To read
the data you should get the gshhs supplement to GMT, the Generic
Mapping Tools (gmt.soest.hawaii.edu).  GSHHS appear in GMT in a
different, netCDF format optimized for plotting as huge polygons
are not as efficient.  For more information about how the GSHHS
data were processed, see Wessel and Smith, 1996, JGR.
Many thanks to Tom Kratzke, Metron Inc., for patiently testing
many draft versions of GSHHS and reporting inconsistencies such as
erratic data points and crossings.

Version 2.0 differs from the previous version 1.x in the following
ways.

1.  Free from internal and external crossings and erratic spikes
    at all five resolutions.
2.  The original Eurasiafrica polygon has now been split into Eurasia
    (polygon # 0) and Africa (polygon # 1) along the Suez canal.
3.  The original Americas polygon has now been split into North America
    (polygon # 2) and South America (polygon # 3) along the Panama canal.
4.  Antarctica is now polygon # 4 and Australia is polygon # 5, in all
    the five resolutions.
5.  Fixed numerous problems, including missing islands and lakes in the
    Amazon and Nile deltas.
6.  Flagged "riverlakes" which are the fat part of major rivers so they
    may easily be identified by users.
7.  Determined container ID for all polygons (== -1 for level 1 polygons)
    which is the ID of the polygon that contains a smaller polygon.
8.  Determined full-resolution ancestor ID for lower res polygons, i.e.,
    the ID of the polygon that was reduced to yield the lower-res version.
9.  Ensured consistency across resolutions (i.e., a feature that
    is an island at full resolution should not become a lake in low!).
10. Sorted tables on level, then on the area of each feature.
11. Made sure no feature is missing in one resolution but
    present in the next lower resolution.
12. Store both the actual area of the lower-res polygons and the area of
    the full-resolution ancestor so users may exclude features that
    represent less that a fraction of the original full area.

There was some duplication and wrong levels assigned to maritime political
boundaries in the Persian Gulf that has been fixed.

These changes required us to enhance the GSHHS C-structure used to read
and write the data.  As of version 2.0 the header structure is

struct GSHHS {	/* Global Self-consistent Hierarchical High-resolution Shorelines */
	int id;		/* Unique polygon id number, starting at 0 */
	int n;		/* Number of points in this polygon */
	int flag;	/* = level + version << 8 + greenwich << 16 + source << 24 + river << 25 */
	/* flag contains 5 items, as follows:
	 * low byte:	level = flag & 255: Values: 1 land, 2 lake, 3 island_in_lake, 4 pond_in_island_in_lake
	 * 2nd byte:	version = (flag >> 8) & 255: Values: Should be 7 for GSHHS release 7 (i.e., version 2.0)
	 * 3rd byte:	greenwich = (flag >> 16) & 1: Values: Greenwich is 1 if Greenwich is crossed
	 * 4th byte:	source = (flag >> 24) & 1: Values: 0 = CIA WDBII, 1 = WVS
	 * 4th byte:	river = (flag >> 25) & 1: Values: 0 = not set, 1 = river-lake and level = 2
	 */
	int west, east, south, north;	/* min/max extent in micro-degrees */
	int area;	/* Area of polygon in 1/10 km^2 */
	int area_full;	/* Area of original full-resolution polygon in 1/10 km^2 */
	int container;	/* Id of container polygon that encloses this polygon (-1 if none) */
	int ancestor;	/* Id of ancestor polygon in the full resolution set that was the source of this polygon (-1 if none) */
};

Some useful information:

A) The binary files were written on an Intel-equipped computer and are thus little-endian.
   If you use the GMT supplement gshhs it will check for endian-ness and if needed will
   byte swab the data.

B) In addition to GSHHS we also distribute the files with political boundaries and
   river lines.  These derive from the WDBII data set.

C) As to the best of our knowledge, the GSHHS data are geodetic longitude, latitude
   locations on the WGS-84 ellipsoid.  This is certainly true of the WVS data (the coastlines).
   Lakes, riverlakes (and river lines and political borders) came from the WDBII data set
   which may have been on WGS072.  The difference in ellipsoid is way less then the data
   uncertainties.  Offsets have been noted between GSHHS and modern GPS positions.

D) Originally, the gshhs_dp tool was used on the full resolution data to produce the lower
   resolution versions.  However, the Douglas-Peucker algorithm often produce polygons with
   self-intersections as well as create segments that intersect other polygons.  These problems
   have been corrected in the GSHHS lower resolutions over the years.  If you use gshhs_dp to
   generate your own lower-resolution data set you should expect these problems.

E) The shapefiles release was made by formatting the GSHHS data using the extended GMT/GIS
   metadata understood by OGR, then using ogr2ogr to build the shapefiles.  Each resolution
   is stored in its own subdirectory (e.g., f, h, i, l, c) and each level (1-4) appears in
   its own shapefile.  Thus, GSHHS_h_L3.shp contains islands in lakes for the high res
   data. Because of GIS limitations some polygons that straddle the Dateline (including
   Antarctica) have been split into two parts (east and west).

Paul Wessel	Primary contact: pwessel@hawaii.edu
Walter H. F. Smith

Reference:
Wessel, P. and Smith, W.H.F., 1996. A global, self-consistent, hierarchical, high-resolution
   shoreline database. J. Geophys. Res., 101(B4): 8741–8743.
