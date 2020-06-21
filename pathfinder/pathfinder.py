def ccw(A, B, C):
    """Tests whether the line formed by A, B, and C is ccw"""
    return (B.x - A.x) * (C.y - A.y) < (B.y - A.y) * (C.x - A.x)

class PathFinder:
    def __init__(self):
        pass

    '''
    Implementation of the funnel algorithm for path finding
    '''
    def find_path_funnel(self, point_dict , edge_path, p, q):

        tail = [p]
        left = []
        right = []

        last_edge_l = None
        last_edge_r = None

        for i,e in enumerate(edge_path):
            p1, p2 = point_dict[e[0]], point_dict[e[1]]


            if p2 == last_edge_l or p1 == last_edge_r or (last_edge_r is None and last_edge_l is None and ccw(tail[-1], p2, p1)):
                p1, p2 = p2, p1


            if len(left) == 0 and p1 != tail[-1]: #or (left[-1] == tail[-1]):
                # If appex is the same as previous left, then add the current point
                left = [p1]
            elif len(left) > 0 and left[-1] != p1:

                if not ccw(tail[-1], p1, left[-1]):

                    last_collision = -1
                    for i,p in enumerate(right):
                        if ccw(tail[-1], p, p1):
                            # Point of right segment is left of point of left segment(violation).
                            # So, add violating vertices to tail
                            tail.append(right[i])
                            last_collision = i

                    if last_collision >= 0:
                        # Collision with one or more previous right points when narrowing funnel
                        left = [p1]
                        right = right[last_collision + 1:]
                    else:
                        # No collisions so we just narrow the funnel
                        left[-1] = p1
                else:
                    # New point opens the funnel and doesn't narrow it.
                    # so append it
                    left.append(p1)


            if len(right) == 0 and p2 != tail[-1]:
                # If appex is the same as previous right, then add the current point
                right = [p2]
            elif len(right) > 0 and right[-1] != p2:

                if not ccw(tail[-1], right[-1], p2):

                    last_collision = -1
                    for i,p in enumerate(left):
                        if ccw(tail[-1], p2, p):
                            # Point of right segment is left of point of left segment(violation)
                            # So, add violating vertices to tail
                            tail.append(left[i])
                            last_collision = i

                    if last_collision >= 0:
                        # Collision with one or more previous left points when narrowing funnel
                        right = [p2]
                        left = left[last_collision + 1:]
                    else:
                        # No collisions so we just narrow the funnel
                        right[-1] = p2
                else:
                    # New point opens the funnel and doesn't narrow it.
                    # so append it
                    right.append(p2)


            last_edge_l = p1
            last_edge_r = p2

        apex = tail[-1]
        # Fix last collisions
        for i, p in enumerate(right):
            if ccw(apex, p, q):
                tail.append(right[i])

        for i,p in enumerate(left):
            if ccw(apex, q, p):
                tail.append(left[i])
        tail.append(q)
        return tail

