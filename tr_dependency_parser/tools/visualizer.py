import spacy
from spacy import displacy
import plotly.graph_objects as go

class parse_visualizer:
    def __init__(self):
        with open("tr_dependency_parser/grammar/grammar.txt", "r") as f:
            lines = f.readlines()
            
        nonterm = set([line.split(" ->")[0] if "#" not in line else "" for line in lines])
        color_dict = {
            "NP" : "turquoise",
            "PRO" : "palevioletred",
            "ADJ" : "lime",
            "VP" : "lightpink",
            "ADV" : "khaki",
            "POSTP" : "cornflowerblue",
            "SG" : "tomato",
            "S" : "tomato",
            "DET" : "limegreen",
            "DAT" : "limegreen",
            "NUM" : "salmon",
            "Q" : "y",
            "GENITIVE" : "green"
        }

        colors = {}
        for nont in nonterm:
            colors[nont] = None
            for key in color_dict.keys():
                if key in nont:
                    colors[nont] = color_dict[key]
                    break
        self.colors = colors
        self.options = {
            "ents" : nonterm,
            "colors" : colors,
            "distance": 200}

    
    def pos_vis(self, sentence, terminals):
        ents = []
        for terminal in terminals:
            ents.append({"start" : terminal.span[0], 
                        "end"   : terminal.span[1], 
                        "label" : terminal.tag })

        doc = {"text" : sentence, "ents" : ents}
        return displacy.render(
            doc, 
            style = "ent",
            options = self.options,
            manual = True
        )
    
    def pos_tree_vis(self, sentence, tokens, tree):
        def get_nodes(node):
            if node.terminal:
                return [node]

            return [node] + get_nodes(node.child1) + get_nodes(node.child2)

        ents = []
        for node in get_nodes(tree):
            ents.append({"start_token" : node.token_range[0], 
                        "end_token"   : node.token_range[1]+1, 
                        "label" : node.tag})
        ents.reverse()
        doc = {"text" : sentence, "spans" : ents, "tokens" : tokens}
        return displacy.render(doc, 
                        style = "span",
                        options = self.options,
                        manual = True,
               )

    def tree_vis(self, sentence, tokens, tree):
        def get_depth(node, counter):
            if node.terminal:
                return counter
                
            return max(get_depth(node.child1, counter + 1), get_depth(node.child2, counter + 1))
        
        def get_coordinates(node, tokens, tot_depth, depth):
            margin_child = tot_depth - depth
            y = margin_child + 1
            
            if node.terminal:
                x = (tokens.index(node.text) + 1) * 2 - 1
                return [{
                    "tag" : node.tag,
                    "text" : node.text,
                    "x" : x,
                    "y" : y,
                    "connectionsx" : [x, x, None],
                    "connectionsy" : [y, y-1, None]
                }]
            
            left_coor = get_coordinates(node.child1, tokens, tot_depth, depth+1)
            right_coor = get_coordinates(node.child2, tokens, tot_depth, depth+1)
            
            x = left_coor[0]["x"] + margin_child
            coord = {
                "tag" : node.tag,
                "x" : x,
                "y" : y,
                "connectionsx" : [x, left_coor[0]["x"], None, x, right_coor[0]["x"], None],
                "connectionsy" : [y, left_coor[0]["y"], None, y, right_coor[0]["y"], None]
            }
            
            return [coord] + [item for item in left_coor] + [item for item in right_coor]

        depth = get_depth(tree, 1)
        coords = get_coordinates(tree, tokens, depth, 1)
        Xe = []
        Ye = []
        Xn = []
        Yn = []
        annotations = []

        Xw = []
        Yw = []
        annotx = []

        font_size=12
        font_color='rgb(250,250,250)'
        for coor in coords:
            Xe += coor["connectionsx"]
            Ye += coor["connectionsy"]
            Xn.append(coor["x"])
            Yn.append(coor["y"])
            annotations.append(
                    dict(
                        text=coor["tag"],
                        x=coor["x"],
                        y=coor["y"],
                        xref='x1', yref='y1',
                        font=dict(color=font_color, size=font_size),
                        showarrow=False)
                )
            
            try:
                if coor["text"] == None: continue
                Xw.append(coor["x"])
                Yw.append(coor["y"]-1)
                annotations.append(
                    dict(
                        text=coor["text"],
                        x=coor["x"],
                        y=coor["y"] - 1,
                        xref='x1', yref='y1',
                        font=dict(color="black", size=18),
                        showarrow=False)
                )
            except:
                pass
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=Xe,
                        y=Ye,
                        mode='lines',
                        line=dict(color='rgb(210,210,210)', width=3),
                        hoverinfo='none'
                        ))

        fig.add_trace(go.Scatter(
            x=Xn,
            y=Yn,
            mode='markers',
            name='Non-terminals',
            marker=dict(symbol='circle-dot',
                        size=72,
                        color='#6175c1',    #'#DB4551',
                        line=dict(color='rgb(50,50,50)', width=1)
                        ),
            hoverinfo='none',
            opacity=1
            ))

        fig.add_trace(go.Scatter(
            x=Xw,
            y=Yw,
            mode='markers',
            name='Termonals',
            marker=dict(symbol='square',
                        size=48,
                        color='#DB4551',    #'#DB4551',
                        line=dict(color='rgb(50,50,50)', width=1),
                        opacity = 0
                        ),
            hoverinfo='none',
            opacity=1
            ))

        axis = dict(showline=False,
                    zeroline=False,
                    showgrid=False,
                    showticklabels=False,
                    )

        fig.update_layout(title= sentence,
                    annotations=annotations,
                    font_size=12,
                    showlegend=False,
                    xaxis=axis,
                    yaxis=axis,
                    margin=dict(l=40, r=40, b=85, t=100),
                    hovermode='closest',
                    plot_bgcolor='rgb(248,248,248)'
                    )
        return fig