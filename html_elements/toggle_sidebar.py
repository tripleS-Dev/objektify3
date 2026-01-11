toggle_sidebar = """
        () => {
          const root = document.querySelector(".gradio-container") || document;
          const btn = root.querySelector('button[aria-label="Toggle Sidebar"]');
          if (btn) btn.click();
        }
        """