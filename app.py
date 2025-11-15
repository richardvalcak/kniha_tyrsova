streamlit.errors.StreamlitInvalidFormCallbackError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).

Traceback:
File "/mount/src/kniha_tyrsova/app.py", line 68, in <module>
    pocet_osob = st.selectbox(
        "Počet ubytovaných osob *",
    ...<3 lines>...
        on_change=lambda: st.rerun()  # HNED aktualizuje formulář!
    )
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/metrics_util.py", line 447, in wrapped_func
    result = non_optional_func(*args, **kwargs)
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/widgets/selectbox.py", line 470, in selectbox
    return self._selectbox(
           ~~~~~~~~~~~~~~~^
        label=label,
        ^^^^^^^^^^^^
    ...<13 lines>...
        ctx=ctx,
        ^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/widgets/selectbox.py", line 509, in _selectbox
    check_widget_policies(
    ~~~~~~~~~~~~~~~~~~~~~^
        self.dg,
        ^^^^^^^^
    ...<2 lines>...
        default_value=None if index == 0 else index,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/lib/policies.py", line 176, in check_widget_policies
    check_callback_rules(dg, on_change)
    ~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/elements/lib/policies.py", line 53, in check_callback_rules
    raise StreamlitInvalidFormCallbackError()
