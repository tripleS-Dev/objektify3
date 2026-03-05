import gradio as gr


def add_class(classes: list[str], size=10):


    classes_normal = (classes + [None] * size)[:size]
    gr.Info(str(classes_normal))

    output = []

    for i in range(10):
        with gr.Tab(label=str(classes_normal[i] if classes_normal[i] else ''), id=i, visible=True) as t: #In here add visibie, Than Bug
            output.append(t)

    return output + [gr.Tabs(selected=int(len(classes))-1)]

def class_tab_visible(classes: list[str], size=10):
    output = []
    classes_normal = (classes + [None] * size)[:size]

    for i in range(10):
        with gr.Tab(visible=True if classes_normal[i] else False, id=i) as t:
            output.append(t)

    return output