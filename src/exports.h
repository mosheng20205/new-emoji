#pragma once
#include "element_types.h"

// Forward declarations (no includes needed for this header)
struct WindowState;

// ── Window management ────────────────────────────────────────────────
HWND __stdcall EU_CreateWindow(const unsigned char* title_bytes, int title_len,
                               int x, int y, int w, int h, Color titlebar_color);
HWND __stdcall EU_CreateWindowDark(const unsigned char* title_bytes, int title_len,
                                   int x, int y, int w, int h, Color titlebar_color);
void __stdcall EU_DestroyWindow(HWND hwnd);
void __stdcall EU_ShowWindow(HWND hwnd, int visible);
void __stdcall EU_SetWindowTitle(HWND hwnd, const unsigned char* bytes, int len);
void __stdcall EU_SetWindowBounds(HWND hwnd, int x, int y, int w, int h);
int  __stdcall EU_GetWindowBounds(HWND hwnd, int* x, int* y, int* w, int* h);

// ── Element creation (return element ID, 0 on failure) ───────────────
int __stdcall EU_CreatePanel(HWND hwnd, int parent_id, int x, int y, int w, int h);
int __stdcall EU_CreateButton(HWND hwnd, int parent_id,
                              const unsigned char* emoji_bytes, int emoji_len,
                              const unsigned char* text_bytes, int text_len,
                              int x, int y, int w, int h);
int __stdcall EU_CreateEditBox(HWND hwnd, int parent_id, int x, int y, int w, int h);
int __stdcall EU_CreateInfoBox(HWND hwnd, int parent_id,
                               const unsigned char* title_bytes, int title_len,
                               const unsigned char* text_bytes, int text_len,
                               int x, int y, int w, int h);
int __stdcall EU_CreateText(HWND hwnd, int parent_id,
                            const unsigned char* text_bytes, int text_len,
                            int x, int y, int w, int h);
int __stdcall EU_CreateLink(HWND hwnd, int parent_id,
                            const unsigned char* text_bytes, int text_len,
                            int x, int y, int w, int h);
int __stdcall EU_CreateIcon(HWND hwnd, int parent_id,
                            const unsigned char* text_bytes, int text_len,
                            int x, int y, int w, int h);
int __stdcall EU_CreateSpace(HWND hwnd, int parent_id, int x, int y, int w, int h);
int __stdcall EU_CreateContainer(HWND hwnd, int parent_id, int x, int y, int w, int h);
int __stdcall EU_CreateLayout(HWND hwnd, int parent_id, int orientation, int gap,
                              int x, int y, int w, int h);
int __stdcall EU_CreateBorder(HWND hwnd, int parent_id, int x, int y, int w, int h);
int __stdcall EU_CreateCheckbox(HWND hwnd, int parent_id,
                                const unsigned char* text_bytes, int text_len,
                                int checked, int x, int y, int w, int h);
int __stdcall EU_CreateCheckboxGroup(HWND hwnd, int parent_id,
                                     const unsigned char* items_bytes, int items_len,
                                     const unsigned char* checked_bytes, int checked_len,
                                     int style_mode, int size, int group_disabled,
                                     int min_checked, int max_checked,
                                     int x, int y, int w, int h);
int __stdcall EU_CreateRadio(HWND hwnd, int parent_id,
                             const unsigned char* text_bytes, int text_len,
                             int checked, int x, int y, int w, int h);
int __stdcall EU_CreateRadioGroup(HWND hwnd, int parent_id,
                                  const unsigned char* items_bytes, int items_len,
                                  const unsigned char* value_bytes, int value_len,
                                  int style_mode, int size, int group_disabled,
                                  int x, int y, int w, int h);
int __stdcall EU_CreateSwitch(HWND hwnd, int parent_id,
                              const unsigned char* text_bytes, int text_len,
                              int checked, int x, int y, int w, int h);
int __stdcall EU_CreateSlider(HWND hwnd, int parent_id,
                              const unsigned char* text_bytes, int text_len,
                              int min_value, int max_value, int value,
                              int x, int y, int w, int h);
int __stdcall EU_CreateInputNumber(HWND hwnd, int parent_id,
                                   const unsigned char* text_bytes, int text_len,
                                   int value, int min_value, int max_value, int step,
                                   int x, int y, int w, int h);
int __stdcall EU_CreateInput(HWND hwnd, int parent_id,
                             const unsigned char* text_bytes, int text_len,
                             const unsigned char* placeholder_bytes, int placeholder_len,
                             const unsigned char* prefix_bytes, int prefix_len,
                             const unsigned char* suffix_bytes, int suffix_len,
                             int clearable,
                             int x, int y, int w, int h);
int __stdcall EU_CreateInputGroup(HWND hwnd, int parent_id,
                                  const unsigned char* value_bytes, int value_len,
                                  const unsigned char* placeholder_bytes, int placeholder_len,
                                  int size, int clearable, int password,
                                  int show_word_limit, int autosize,
                                  int min_rows, int max_rows,
                                  int x, int y, int w, int h);
int __stdcall EU_CreateInputTag(HWND hwnd, int parent_id,
                                const unsigned char* tags_bytes, int tags_len,
                                const unsigned char* placeholder_bytes, int placeholder_len,
                                int x, int y, int w, int h);
int __stdcall EU_CreateSelect(HWND hwnd, int parent_id,
                              const unsigned char* text_bytes, int text_len,
                              const unsigned char* options_bytes, int options_len,
                              int selected_index, int x, int y, int w, int h);
int __stdcall EU_CreateSelectV2(HWND hwnd, int parent_id,
                                const unsigned char* text_bytes, int text_len,
                                const unsigned char* options_bytes, int options_len,
                                int selected_index, int visible_count,
                                int x, int y, int w, int h);
int __stdcall EU_CreateRate(HWND hwnd, int parent_id,
                            const unsigned char* text_bytes, int text_len,
                            int value, int max_value,
                            int x, int y, int w, int h);
int __stdcall EU_CreateColorPicker(HWND hwnd, int parent_id,
                                   const unsigned char* text_bytes, int text_len,
                                   Color value, int x, int y, int w, int h);
int __stdcall EU_CreateTag(HWND hwnd, int parent_id,
                           const unsigned char* text_bytes, int text_len,
                           int tag_type, int effect, int closable,
                           int x, int y, int w, int h);
int __stdcall EU_CreateBadge(HWND hwnd, int parent_id,
                             const unsigned char* text_bytes, int text_len,
                             const unsigned char* value_bytes, int value_len,
                             int max_value, int dot,
                             int x, int y, int w, int h);
int __stdcall EU_CreateProgress(HWND hwnd, int parent_id,
                                const unsigned char* text_bytes, int text_len,
                                int percentage, int status,
                                int x, int y, int w, int h);
int __stdcall EU_CreateAvatar(HWND hwnd, int parent_id,
                              const unsigned char* text_bytes, int text_len,
                              int shape, int x, int y, int w, int h);
int __stdcall EU_CreateEmpty(HWND hwnd, int parent_id,
                             const unsigned char* title_bytes, int title_len,
                             const unsigned char* desc_bytes, int desc_len,
                             int x, int y, int w, int h);
int __stdcall EU_CreateSkeleton(HWND hwnd, int parent_id,
                                int rows, int animated,
                                int x, int y, int w, int h);
int __stdcall EU_CreateDescriptions(HWND hwnd, int parent_id,
                                    const unsigned char* title_bytes, int title_len,
                                    const unsigned char* items_bytes, int items_len,
                                    int columns, int bordered,
                                    int x, int y, int w, int h);
int __stdcall EU_CreateTable(HWND hwnd, int parent_id,
                             const unsigned char* columns_bytes, int columns_len,
                             const unsigned char* rows_bytes, int rows_len,
                             int striped, int bordered,
                             int x, int y, int w, int h);
int __stdcall EU_CreateCard(HWND hwnd, int parent_id,
                            const unsigned char* title_bytes, int title_len,
                            const unsigned char* body_bytes, int body_len,
                            int shadow, int x, int y, int w, int h);
int __stdcall EU_CreateCollapse(HWND hwnd, int parent_id,
                                const unsigned char* items_bytes, int items_len,
                                int active_index, int accordion,
                                int x, int y, int w, int h);
int __stdcall EU_CreateTimeline(HWND hwnd, int parent_id,
                                const unsigned char* items_bytes, int items_len,
                                int x, int y, int w, int h);
int __stdcall EU_CreateStatistic(HWND hwnd, int parent_id,
                                 const unsigned char* title_bytes, int title_len,
                                 const unsigned char* value_bytes, int value_len,
                                 const unsigned char* prefix_bytes, int prefix_len,
                                 const unsigned char* suffix_bytes, int suffix_len,
                                 int x, int y, int w, int h);
int __stdcall EU_CreateKpiCard(HWND hwnd, int parent_id,
                               const unsigned char* title_bytes, int title_len,
                               const unsigned char* value_bytes, int value_len,
                               const unsigned char* subtitle_bytes, int subtitle_len,
                               const unsigned char* trend_bytes, int trend_len,
                               int trend_type, int x, int y, int w, int h);
int __stdcall EU_CreateTrend(HWND hwnd, int parent_id,
                             const unsigned char* title_bytes, int title_len,
                             const unsigned char* value_bytes, int value_len,
                             const unsigned char* percent_bytes, int percent_len,
                             const unsigned char* detail_bytes, int detail_len,
                             int direction, int x, int y, int w, int h);
int __stdcall EU_CreateStatusDot(HWND hwnd, int parent_id,
                                 const unsigned char* label_bytes, int label_len,
                                 const unsigned char* desc_bytes, int desc_len,
                                 int status, int x, int y, int w, int h);
int __stdcall EU_CreateGauge(HWND hwnd, int parent_id,
                             const unsigned char* title_bytes, int title_len,
                             int value,
                             const unsigned char* caption_bytes, int caption_len,
                             int status, int x, int y, int w, int h);
int __stdcall EU_CreateRingProgress(HWND hwnd, int parent_id,
                                    const unsigned char* title_bytes, int title_len,
                                    int value,
                                    const unsigned char* label_bytes, int label_len,
                                    int status, int x, int y, int w, int h);
int __stdcall EU_CreateBulletProgress(HWND hwnd, int parent_id,
                                      const unsigned char* title_bytes, int title_len,
                                      const unsigned char* desc_bytes, int desc_len,
                                      int value, int target, int status,
                                      int x, int y, int w, int h);
int __stdcall EU_CreateLineChart(HWND hwnd, int parent_id,
                                 const unsigned char* title_bytes, int title_len,
                                 const unsigned char* points_bytes, int points_len,
                                 int chart_style, int x, int y, int w, int h);
int __stdcall EU_CreateBarChart(HWND hwnd, int parent_id,
                                const unsigned char* title_bytes, int title_len,
                                const unsigned char* bars_bytes, int bars_len,
                                int orientation, int x, int y, int w, int h);
int __stdcall EU_CreateDonutChart(HWND hwnd, int parent_id,
                                  const unsigned char* title_bytes, int title_len,
                                  const unsigned char* slices_bytes, int slices_len,
                                  int active_index, int x, int y, int w, int h);
int __stdcall EU_CreateDivider(HWND hwnd, int parent_id,
                               const unsigned char* text_bytes, int text_len,
                               int direction, int content_position,
                               int x, int y, int w, int h);
int __stdcall EU_CreateCalendar(HWND hwnd, int parent_id,
                                int year, int month, int selected_day,
                                int x, int y, int w, int h);
int __stdcall EU_CreateTree(HWND hwnd, int parent_id,
                            const unsigned char* items_bytes, int items_len,
                            int selected_index,
                            int x, int y, int w, int h);
int __stdcall EU_CreateTreeSelect(HWND hwnd, int parent_id,
                                  const unsigned char* items_bytes, int items_len,
                                  int selected_index,
                                  int x, int y, int w, int h);
int __stdcall EU_CreateTransfer(HWND hwnd, int parent_id,
                                const unsigned char* left_bytes, int left_len,
                                const unsigned char* right_bytes, int right_len,
                                int x, int y, int w, int h);
int __stdcall EU_CreateAutocomplete(HWND hwnd, int parent_id,
                                    const unsigned char* value_bytes, int value_len,
                                    const unsigned char* suggestions_bytes, int suggestions_len,
                                    int x, int y, int w, int h);
int __stdcall EU_CreateMentions(HWND hwnd, int parent_id,
                                const unsigned char* value_bytes, int value_len,
                                const unsigned char* suggestions_bytes, int suggestions_len,
                                int x, int y, int w, int h);
int __stdcall EU_CreateCascader(HWND hwnd, int parent_id,
                                const unsigned char* options_bytes, int options_len,
                                const unsigned char* selected_bytes, int selected_len,
                                int x, int y, int w, int h);
int __stdcall EU_CreateDatePicker(HWND hwnd, int parent_id,
                                  int year, int month, int selected_day,
                                  int x, int y, int w, int h);
int __stdcall EU_CreateTimePicker(HWND hwnd, int parent_id,
                                  int hour, int minute,
                                  int x, int y, int w, int h);
int __stdcall EU_CreateDateTimePicker(HWND hwnd, int parent_id,
                                      int year, int month, int day,
                                      int hour, int minute,
                                      int x, int y, int w, int h);
int __stdcall EU_CreateTimeSelect(HWND hwnd, int parent_id,
                                  int hour, int minute,
                                  int x, int y, int w, int h);
int __stdcall EU_CreateDropdown(HWND hwnd, int parent_id,
                                const unsigned char* text_bytes, int text_len,
                                const unsigned char* items_bytes, int items_len,
                                int selected_index,
                                int x, int y, int w, int h);
int __stdcall EU_CreateMenu(HWND hwnd, int parent_id,
                            const unsigned char* items_bytes, int items_len,
                            int active_index, int orientation,
                            int x, int y, int w, int h);
int __stdcall EU_CreateAnchor(HWND hwnd, int parent_id,
                              const unsigned char* items_bytes, int items_len,
                              int active_index,
                              int x, int y, int w, int h);
int __stdcall EU_CreateBacktop(HWND hwnd, int parent_id,
                               const unsigned char* text_bytes, int text_len,
                               int x, int y, int w, int h);
int __stdcall EU_CreateSegmented(HWND hwnd, int parent_id,
                                 const unsigned char* items_bytes, int items_len,
                                 int active_index,
                                 int x, int y, int w, int h);
int __stdcall EU_CreatePageHeader(HWND hwnd, int parent_id,
                                  const unsigned char* title_bytes, int title_len,
                                  const unsigned char* subtitle_bytes, int subtitle_len,
                                  const unsigned char* back_bytes, int back_len,
                                  int x, int y, int w, int h);
int __stdcall EU_CreateAffix(HWND hwnd, int parent_id,
                             const unsigned char* title_bytes, int title_len,
                             const unsigned char* body_bytes, int body_len,
                             int offset,
                             int x, int y, int w, int h);
int __stdcall EU_CreateWatermark(HWND hwnd, int parent_id,
                                 const unsigned char* content_bytes, int content_len,
                                 int gap_x, int gap_y,
                                 int x, int y, int w, int h);
int __stdcall EU_CreateTour(HWND hwnd, int parent_id,
                            const unsigned char* steps_bytes, int steps_len,
                            int active_index, int open,
                            int x, int y, int w, int h);
int __stdcall EU_CreateImage(HWND hwnd, int parent_id,
                             const unsigned char* src_bytes, int src_len,
                             const unsigned char* alt_bytes, int alt_len,
                             int fit,
                             int x, int y, int w, int h);
int __stdcall EU_CreateCarousel(HWND hwnd, int parent_id,
                                const unsigned char* items_bytes, int items_len,
                                int active_index, int indicator_position,
                                int x, int y, int w, int h);
int __stdcall EU_CreateUpload(HWND hwnd, int parent_id,
                              const unsigned char* title_bytes, int title_len,
                              const unsigned char* tip_bytes, int tip_len,
                              const unsigned char* files_bytes, int files_len,
                              int x, int y, int w, int h);
int __stdcall EU_CreateInfiniteScroll(HWND hwnd, int parent_id,
                                      const unsigned char* items_bytes, int items_len,
                                      int x, int y, int w, int h);
int __stdcall EU_CreateBreadcrumb(HWND hwnd, int parent_id,
                                  const unsigned char* items_bytes, int items_len,
                                  const unsigned char* separator_bytes, int separator_len,
                                  int current_index, int x, int y, int w, int h);
int __stdcall EU_CreateTabs(HWND hwnd, int parent_id,
                            const unsigned char* items_bytes, int items_len,
                            int active_index, int tab_type,
                            int x, int y, int w, int h);
int __stdcall EU_CreatePagination(HWND hwnd, int parent_id,
                                  int total, int page_size, int current_page,
                                  int x, int y, int w, int h);
int __stdcall EU_CreateSteps(HWND hwnd, int parent_id,
                             const unsigned char* items_bytes, int items_len,
                             int active_index, int x, int y, int w, int h);
int __stdcall EU_CreateAlert(HWND hwnd, int parent_id,
                             const unsigned char* title_bytes, int title_len,
                             const unsigned char* desc_bytes, int desc_len,
                             int alert_type, int effect, int closable,
                             int x, int y, int w, int h);
int __stdcall EU_CreateResult(HWND hwnd, int parent_id,
                              const unsigned char* title_bytes, int title_len,
                              const unsigned char* subtitle_bytes, int subtitle_len,
                              int result_type,
                              int x, int y, int w, int h);
int __stdcall EU_CreateNotification(HWND hwnd, int parent_id,
                                    const unsigned char* title_bytes, int title_len,
                                    const unsigned char* body_bytes, int body_len,
                                    int notify_type, int closable,
                                    int x, int y, int w, int h);
int __stdcall EU_ShowMessage(HWND hwnd,
                             const unsigned char* text_bytes, int text_len,
                             int message_type, int closable, int center, int rich,
                             int duration_ms, int offset);
int __stdcall EU_ShowNotification(HWND hwnd,
                                  const unsigned char* title_bytes, int title_len,
                                  const unsigned char* body_bytes, int body_len,
                                  int notify_type, int closable, int duration_ms,
                                  int placement, int offset, int rich, int w, int h);
int __stdcall EU_CreateLoading(HWND hwnd, int parent_id,
                               const unsigned char* text_bytes, int text_len,
                               int active,
                               int x, int y, int w, int h);
int __stdcall EU_CreateDialog(HWND hwnd,
                              const unsigned char* title_bytes, int title_len,
                              const unsigned char* body_bytes, int body_len,
                              int modal, int closable,
                              int w, int h);
int __stdcall EU_CreateDrawer(HWND hwnd,
                              const unsigned char* title_bytes, int title_len,
                              const unsigned char* body_bytes, int body_len,
                              int placement, int modal, int closable,
                              int size);
int __stdcall EU_CreateTooltip(HWND hwnd, int parent_id,
                               const unsigned char* label_bytes, int label_len,
                               const unsigned char* content_bytes, int content_len,
                               int placement,
                               int x, int y, int w, int h);
int __stdcall EU_CreatePopover(HWND hwnd, int parent_id,
                               const unsigned char* label_bytes, int label_len,
                               const unsigned char* title_bytes, int title_len,
                               const unsigned char* content_bytes, int content_len,
                               int placement,
                               int x, int y, int w, int h);
int __stdcall EU_CreatePopconfirm(HWND hwnd, int parent_id,
                                  const unsigned char* label_bytes, int label_len,
                                  const unsigned char* title_bytes, int title_len,
                                  const unsigned char* content_bytes, int content_len,
                                  const unsigned char* confirm_bytes, int confirm_len,
                                  const unsigned char* cancel_bytes, int cancel_len,
                                  int placement,
                                  int x, int y, int w, int h);
int __stdcall EU_ShowMessageBox(HWND hwnd,
                                const unsigned char* title_bytes, int title_len,
                                const unsigned char* text_bytes, int text_len,
                                const unsigned char* confirm_bytes, int confirm_len,
                                MessageBoxResultCallback cb);
int __stdcall EU_ShowConfirmBox(HWND hwnd,
                                const unsigned char* title_bytes, int title_len,
                                const unsigned char* text_bytes, int text_len,
                                const unsigned char* confirm_bytes, int confirm_len,
                                const unsigned char* cancel_bytes, int cancel_len,
                                MessageBoxResultCallback cb);
int __stdcall EU_ShowMessageBoxEx(HWND hwnd,
                                  const unsigned char* title_bytes, int title_len,
                                  const unsigned char* text_bytes, int text_len,
                                  const unsigned char* confirm_bytes, int confirm_len,
                                  const unsigned char* cancel_bytes, int cancel_len,
                                  int box_type, int show_cancel, int center, int rich,
                                  int distinguish_cancel_and_close,
                                  MessageBoxExCallback cb);
int __stdcall EU_ShowPromptBox(HWND hwnd,
                               const unsigned char* title_bytes, int title_len,
                               const unsigned char* text_bytes, int text_len,
                               const unsigned char* placeholder_bytes, int placeholder_len,
                               const unsigned char* value_bytes, int value_len,
                               const unsigned char* pattern_bytes, int pattern_len,
                               const unsigned char* error_bytes, int error_len,
                               const unsigned char* confirm_bytes, int confirm_len,
                               const unsigned char* cancel_bytes, int cancel_len,
                               int box_type, int center, int rich,
                               int distinguish_cancel_and_close,
                               MessageBoxExCallback cb);

// ── Element properties ───────────────────────────────────────────────
void __stdcall EU_SetElementText(HWND hwnd, int element_id, const unsigned char* bytes, int len);
int  __stdcall EU_GetElementText(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size);
void __stdcall EU_SetElementBounds(HWND hwnd, int element_id, int x, int y, int w, int h);
int  __stdcall EU_GetElementBounds(HWND hwnd, int element_id, int* x, int* y, int* w, int* h);
void __stdcall EU_SetElementVisible(HWND hwnd, int element_id, int visible);
int  __stdcall EU_GetElementVisible(HWND hwnd, int element_id);
void __stdcall EU_SetElementEnabled(HWND hwnd, int element_id, int enabled);
int  __stdcall EU_GetElementEnabled(HWND hwnd, int element_id);
void __stdcall EU_SetElementColor(HWND hwnd, int element_id, Color bg, Color fg);
void __stdcall EU_SetElementFont(HWND hwnd, int element_id, const unsigned char* font_bytes, int font_len, float size);
void __stdcall EU_SetTextOptions(HWND hwnd, int element_id, int align, int valign, int wrap, int ellipsis);
int  __stdcall EU_GetTextOptions(HWND hwnd, int element_id, int* align, int* valign, int* wrap, int* ellipsis);
void __stdcall EU_SetLinkOptions(HWND hwnd, int element_id, int type, int underline, int auto_open, int visited);
int  __stdcall EU_GetLinkOptions(HWND hwnd, int element_id, int* type, int* underline, int* auto_open, int* visited);
void __stdcall EU_SetLinkContent(HWND hwnd, int element_id,
                                 const unsigned char* prefix_bytes, int prefix_len,
                                 const unsigned char* suffix_bytes, int suffix_len,
                                 const unsigned char* href_bytes, int href_len,
                                 const unsigned char* target_bytes, int target_len);
int  __stdcall EU_GetLinkContent(HWND hwnd, int element_id,
                                 unsigned char* prefix_buffer, int prefix_buffer_size,
                                 unsigned char* suffix_buffer, int suffix_buffer_size,
                                 unsigned char* href_buffer, int href_buffer_size,
                                 unsigned char* target_buffer, int target_buffer_size);
void __stdcall EU_SetLinkVisited(HWND hwnd, int element_id, int visited);
int  __stdcall EU_GetLinkVisited(HWND hwnd, int element_id);
void __stdcall EU_SetIconOptions(HWND hwnd, int element_id, float scale, float rotation_degrees);
int  __stdcall EU_GetIconOptions(HWND hwnd, int element_id, float* scale, float* rotation_degrees);
void __stdcall EU_SetPanelStyle(HWND hwnd, int element_id, Color bg, Color border, float border_width, float radius, int padding);
int  __stdcall EU_GetPanelStyle(HWND hwnd, int element_id, Color* bg, Color* border, float* border_width, float* radius, int* padding);
void __stdcall EU_SetPanelLayout(HWND hwnd, int element_id, int fill_parent, int content_layout);
int  __stdcall EU_GetPanelLayout(HWND hwnd, int element_id, int* fill_parent, int* content_layout);
void __stdcall EU_SetLayoutOptions(HWND hwnd, int element_id, int orientation, int gap, int stretch, int align, int wrap);
int  __stdcall EU_GetLayoutOptions(HWND hwnd, int element_id, int* orientation, int* gap, int* stretch, int* align, int* wrap);
void __stdcall EU_SetLayoutChildWeight(HWND hwnd, int layout_id, int child_id, int weight);
int  __stdcall EU_GetLayoutChildWeight(HWND hwnd, int layout_id, int child_id);
void __stdcall EU_SetBorderOptions(HWND hwnd, int element_id, int sides, Color color, float width, float radius,
                                   const unsigned char* title_bytes, int title_len);
int  __stdcall EU_GetBorderOptions(HWND hwnd, int element_id, int* sides, Color* color, float* width, float* radius);
void __stdcall EU_SetBorderDashed(HWND hwnd, int element_id, int dashed);
int  __stdcall EU_GetBorderDashed(HWND hwnd, int element_id);
void __stdcall EU_SetInfoBoxText(HWND hwnd, int element_id,
                                 const unsigned char* title_bytes, int title_len,
                                 const unsigned char* body_bytes, int body_len);
void __stdcall EU_SetInfoBoxOptions(HWND hwnd, int element_id, int type, int closable, Color accent,
                                   const unsigned char* icon_bytes, int icon_len);
void __stdcall EU_SetInfoBoxClosed(HWND hwnd, int element_id, int closed);
int  __stdcall EU_GetInfoBoxClosed(HWND hwnd, int element_id);
int  __stdcall EU_GetInfoBoxPreferredHeight(HWND hwnd, int element_id);
void __stdcall EU_SetSpaceSize(HWND hwnd, int element_id, int w, int h);
int  __stdcall EU_GetSpaceSize(HWND hwnd, int element_id, int* w, int* h);
void __stdcall EU_SetDividerOptions(HWND hwnd, int element_id,
                                    int direction, int content_position, Color color,
                                    float width, int dashed,
                                    const unsigned char* text_bytes, int text_len);
int  __stdcall EU_GetDividerOptions(HWND hwnd, int element_id,
                                    int* direction, int* content_position, Color* color,
                                    float* width, int* dashed);
void __stdcall EU_SetDividerSpacing(HWND hwnd, int element_id, int margin, int gap);
int  __stdcall EU_GetDividerSpacing(HWND hwnd, int element_id, int* margin, int* gap);
void __stdcall EU_SetButtonEmoji(HWND hwnd, int element_id, const unsigned char* bytes, int len);
void __stdcall EU_SetButtonVariant(HWND hwnd, int element_id, int variant);
int  __stdcall EU_GetButtonState(HWND hwnd, int element_id, int* pressed, int* focused, int* variant);
void __stdcall EU_SetButtonOptions(HWND hwnd, int element_id,
                                   int variant, int plain, int round,
                                   int circle, int loading, int size);
int  __stdcall EU_GetButtonOptions(HWND hwnd, int element_id,
                                   int* variant, int* plain, int* round,
                                   int* circle, int* loading, int* size);
void __stdcall EU_SetEditBoxText(HWND hwnd, int element_id, const unsigned char* bytes, int len);
void __stdcall EU_SetEditBoxOptions(HWND hwnd, int element_id, int readonly, int password, int multiline,
                                    Color focus_border, const unsigned char* placeholder_bytes, int placeholder_len);
int  __stdcall EU_GetEditBoxOptions(HWND hwnd, int element_id, int* readonly, int* password, int* multiline,
                                   Color* focus_border);
int  __stdcall EU_GetEditBoxState(HWND hwnd, int element_id, int* cursor, int* sel_start, int* sel_end, int* text_length);
int  __stdcall EU_GetEditBoxText(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size);
void __stdcall EU_SetEditBoxTextCallback(HWND hwnd, int element_id, ElementTextCallback cb);
void __stdcall EU_SetElementFocus(HWND hwnd, int element_id);
void __stdcall EU_InvalidateElement(HWND hwnd, int element_id);
void __stdcall EU_SetCheckboxChecked(HWND hwnd, int element_id, int checked);
int  __stdcall EU_GetCheckboxChecked(HWND hwnd, int element_id);
void __stdcall EU_SetCheckboxIndeterminate(HWND hwnd, int element_id, int indeterminate);
int  __stdcall EU_GetCheckboxIndeterminate(HWND hwnd, int element_id);
void __stdcall EU_SetCheckboxOptions(HWND hwnd, int element_id, int border, int size);
int  __stdcall EU_GetCheckboxOptions(HWND hwnd, int element_id, int* border, int* size);
void __stdcall EU_SetCheckboxGroupItems(HWND hwnd, int element_id,
                                        const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetCheckboxGroupValue(HWND hwnd, int element_id,
                                        const unsigned char* values_bytes, int values_len);
int  __stdcall EU_GetCheckboxGroupValue(HWND hwnd, int element_id,
                                        unsigned char* buffer, int buffer_size);
void __stdcall EU_SetCheckboxGroupOptions(HWND hwnd, int element_id,
                                          int group_disabled, int style_mode, int size,
                                          int min_checked, int max_checked);
int  __stdcall EU_GetCheckboxGroupOptions(HWND hwnd, int element_id,
                                          int* group_disabled, int* style_mode, int* size,
                                          int* min_checked, int* max_checked);
int  __stdcall EU_GetCheckboxGroupState(HWND hwnd, int element_id,
                                        int* checked_count, int* item_count,
                                        int* disabled_count, int* group_disabled,
                                        int* style_mode, int* size,
                                        int* min_checked, int* max_checked,
                                        int* hover_index, int* press_index,
                                        int* focus_index, int* last_action);
void __stdcall EU_SetCheckboxGroupChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetRadioChecked(HWND hwnd, int element_id, int checked);
int  __stdcall EU_GetRadioChecked(HWND hwnd, int element_id);
void __stdcall EU_SetRadioGroup(HWND hwnd, int element_id,
                                const unsigned char* group_bytes, int group_len);
int  __stdcall EU_GetRadioGroup(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size);
void __stdcall EU_SetRadioValue(HWND hwnd, int element_id,
                                const unsigned char* value_bytes, int value_len);
int  __stdcall EU_GetRadioValue(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size);
void __stdcall EU_SetRadioOptions(HWND hwnd, int element_id, int border, int size);
int  __stdcall EU_GetRadioOptions(HWND hwnd, int element_id, int* border, int* size);
void __stdcall EU_SetRadioGroupItems(HWND hwnd, int element_id,
                                     const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetRadioGroupValue(HWND hwnd, int element_id,
                                     const unsigned char* value_bytes, int value_len);
int  __stdcall EU_GetRadioGroupValue(HWND hwnd, int element_id,
                                     unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetRadioGroupSelectedIndex(HWND hwnd, int element_id);
void __stdcall EU_SetRadioGroupOptions(HWND hwnd, int element_id,
                                       int group_disabled, int style_mode, int size);
int  __stdcall EU_GetRadioGroupOptions(HWND hwnd, int element_id,
                                       int* group_disabled, int* style_mode, int* size);
int  __stdcall EU_GetRadioGroupState(HWND hwnd, int element_id,
                                     int* selected_index, int* item_count,
                                     int* disabled_count, int* group_disabled,
                                     int* style_mode, int* size,
                                     int* hover_index, int* press_index,
                                     int* last_action);
void __stdcall EU_SetRadioGroupChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetSwitchChecked(HWND hwnd, int element_id, int checked);
int  __stdcall EU_GetSwitchChecked(HWND hwnd, int element_id);
void __stdcall EU_SetSwitchLoading(HWND hwnd, int element_id, int loading);
int  __stdcall EU_GetSwitchLoading(HWND hwnd, int element_id);
void __stdcall EU_SetSwitchTexts(HWND hwnd, int element_id,
                                 const unsigned char* active_bytes, int active_len,
                                 const unsigned char* inactive_bytes, int inactive_len);
int  __stdcall EU_GetSwitchOptions(HWND hwnd, int element_id,
                                  int* checked, int* loading, int* has_active_text, int* has_inactive_text);
void __stdcall EU_SetSwitchActiveColor(HWND hwnd, int element_id, Color color);
Color __stdcall EU_GetSwitchActiveColor(HWND hwnd, int element_id);
void __stdcall EU_SetSwitchInactiveColor(HWND hwnd, int element_id, Color color);
Color __stdcall EU_GetSwitchInactiveColor(HWND hwnd, int element_id);
void __stdcall EU_SetSwitchValue(HWND hwnd, int element_id, int value);
int  __stdcall EU_GetSwitchValue(HWND hwnd, int element_id);
void __stdcall EU_SetSwitchSize(HWND hwnd, int element_id, int size);
int  __stdcall EU_GetSwitchSize(HWND hwnd, int element_id);
void __stdcall EU_SetSliderRange(HWND hwnd, int element_id, int min_value, int max_value);
void __stdcall EU_SetSliderValue(HWND hwnd, int element_id, int value);
int  __stdcall EU_GetSliderValue(HWND hwnd, int element_id);
void __stdcall EU_SetSliderOptions(HWND hwnd, int element_id, int step, int show_tooltip);
int  __stdcall EU_GetSliderStep(HWND hwnd, int element_id);
int  __stdcall EU_GetSliderOptions(HWND hwnd, int element_id, int* min_value, int* max_value, int* step, int* show_tooltip);
void __stdcall EU_SetSliderRangeValue(HWND hwnd, int element_id, int start_value, int end_value);
int  __stdcall EU_GetSliderRangeValue(HWND hwnd, int element_id, int* start_value, int* end_value);
void __stdcall EU_SetSliderRangeMode(HWND hwnd, int element_id, int enabled, int start_value, int end_value);
int  __stdcall EU_GetSliderRangeMode(HWND hwnd, int element_id, int* enabled, int* start_value, int* end_value);
void __stdcall EU_SetSliderValueCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetInputNumberRange(HWND hwnd, int element_id, int min_value, int max_value);
void __stdcall EU_SetInputNumberStep(HWND hwnd, int element_id, int step);
void __stdcall EU_SetInputNumberValue(HWND hwnd, int element_id, int value);
int  __stdcall EU_GetInputNumberValue(HWND hwnd, int element_id);
int  __stdcall EU_GetInputNumberCanStep(HWND hwnd, int element_id, int delta);
int  __stdcall EU_GetInputNumberOptions(HWND hwnd, int element_id, int* min_value, int* max_value, int* step);
void __stdcall EU_SetInputNumberPrecision(HWND hwnd, int element_id, int precision);
int  __stdcall EU_GetInputNumberPrecision(HWND hwnd, int element_id);
int  __stdcall EU_SetInputNumberText(HWND hwnd, int element_id,
                                     const unsigned char* value_bytes, int value_len);
int  __stdcall EU_GetInputNumberText(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetInputNumberState(HWND hwnd, int element_id,
                                      int* precision, int* editing, int* valid,
                                      int* can_decrease, int* can_increase);
void __stdcall EU_SetInputNumberValueCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetInputNumberStepStrictly(HWND hwnd, int element_id, int strict);
int  __stdcall EU_GetInputNumberStepStrictly(HWND hwnd, int element_id);
void __stdcall EU_SetInputValue(HWND hwnd, int element_id,
                                const unsigned char* value_bytes, int value_len);
int  __stdcall EU_GetInputValue(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size);
void __stdcall EU_SetInputPlaceholder(HWND hwnd, int element_id,
                                      const unsigned char* placeholder_bytes, int placeholder_len);
void __stdcall EU_SetInputAffixes(HWND hwnd, int element_id,
                                  const unsigned char* prefix_bytes, int prefix_len,
                                  const unsigned char* suffix_bytes, int suffix_len);
void __stdcall EU_SetInputIcons(HWND hwnd, int element_id,
                                const unsigned char* prefix_icon_bytes, int prefix_icon_len,
                                const unsigned char* suffix_icon_bytes, int suffix_icon_len);
int  __stdcall EU_GetInputIcons(HWND hwnd, int element_id,
                                unsigned char* prefix_icon_buffer, int prefix_icon_buffer_size,
                                unsigned char* suffix_icon_buffer, int suffix_icon_buffer_size);
void __stdcall EU_SetInputClearable(HWND hwnd, int element_id, int clearable);
void __stdcall EU_SetInputOptions(HWND hwnd, int element_id, int readonly, int password, int multiline, int validate_state);
void __stdcall EU_SetInputVisualOptions(HWND hwnd, int element_id,
                                        int size, int show_password_toggle,
                                        int show_word_limit, int autosize,
                                        int min_rows, int max_rows);
int  __stdcall EU_GetInputVisualOptions(HWND hwnd, int element_id,
                                        int* size, int* show_password_toggle,
                                        int* show_word_limit, int* autosize,
                                        int* min_rows, int* max_rows);
void __stdcall EU_SetInputSelection(HWND hwnd, int element_id, int start, int end);
int  __stdcall EU_GetInputSelection(HWND hwnd, int element_id, int* start, int* end);
void __stdcall EU_SetInputContextMenuEnabled(HWND hwnd, int element_id, int enabled);
int  __stdcall EU_GetInputContextMenuEnabled(HWND hwnd, int element_id);
int  __stdcall EU_GetInputState(HWND hwnd, int element_id, int* cursor, int* length, int* clearable, int* readonly, int* password, int* multiline, int* validate_state);
void __stdcall EU_SetInputMaxLength(HWND hwnd, int element_id, int max_length);
int  __stdcall EU_GetInputMaxLength(HWND hwnd, int element_id);
void __stdcall EU_SetInputTextCallback(HWND hwnd, int element_id, ElementTextCallback cb);
void __stdcall EU_SetInputGroupValue(HWND hwnd, int element_id,
                                     const unsigned char* value_bytes, int value_len);
int  __stdcall EU_GetInputGroupValue(HWND hwnd, int element_id,
                                     unsigned char* buffer, int buffer_size);
void __stdcall EU_SetInputGroupOptions(HWND hwnd, int element_id,
                                       int size, int clearable, int password,
                                       int show_word_limit, int autosize,
                                       int min_rows, int max_rows);
int  __stdcall EU_GetInputGroupOptions(HWND hwnd, int element_id,
                                       int* size, int* clearable, int* password,
                                       int* show_word_limit, int* autosize,
                                       int* min_rows, int* max_rows);
void __stdcall EU_SetInputGroupTextAddon(HWND hwnd, int element_id, int side,
                                         const unsigned char* text_bytes, int text_len);
void __stdcall EU_SetInputGroupButtonAddon(HWND hwnd, int element_id, int side,
                                           const unsigned char* emoji_bytes, int emoji_len,
                                           const unsigned char* text_bytes, int text_len,
                                           int variant);
void __stdcall EU_SetInputGroupSelectAddon(HWND hwnd, int element_id, int side,
                                           const unsigned char* items_bytes, int items_len,
                                           int selected_index,
                                           const unsigned char* placeholder_bytes, int placeholder_len);
void __stdcall EU_ClearInputGroupAddon(HWND hwnd, int element_id, int side);
int  __stdcall EU_GetInputGroupInputElementId(HWND hwnd, int element_id);
int  __stdcall EU_GetInputGroupAddonElementId(HWND hwnd, int element_id, int side);
void __stdcall EU_SetInputTagTags(HWND hwnd, int element_id,
                                  const unsigned char* tags_bytes, int tags_len);
void __stdcall EU_SetInputTagPlaceholder(HWND hwnd, int element_id,
                                         const unsigned char* placeholder_bytes, int placeholder_len);
void __stdcall EU_SetInputTagOptions(HWND hwnd, int element_id, int max_count, int allow_duplicates);
int  __stdcall EU_GetInputTagCount(HWND hwnd, int element_id);
int  __stdcall EU_GetInputTagOptions(HWND hwnd, int element_id, int* max_count, int* allow_duplicates);
int  __stdcall EU_AddInputTagItem(HWND hwnd, int element_id,
                                  const unsigned char* tag_bytes, int tag_len);
int  __stdcall EU_RemoveInputTagItem(HWND hwnd, int element_id, int tag_index);
void __stdcall EU_SetInputTagInputValue(HWND hwnd, int element_id,
                                        const unsigned char* value_bytes, int value_len);
int  __stdcall EU_GetInputTagInputValue(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetInputTagItem(HWND hwnd, int element_id, int tag_index, unsigned char* buffer, int buffer_size);
void __stdcall EU_SetInputTagChangeCallback(HWND hwnd, int element_id, ElementTextCallback cb);
void __stdcall EU_SetSelectOptions(HWND hwnd, int element_id,
                                   const unsigned char* options_bytes, int options_len);
void __stdcall EU_SetSelectIndex(HWND hwnd, int element_id, int index);
int  __stdcall EU_GetSelectIndex(HWND hwnd, int element_id);
void __stdcall EU_SetSelectOpen(HWND hwnd, int element_id, int open);
int  __stdcall EU_GetSelectOpen(HWND hwnd, int element_id);
void __stdcall EU_SetSelectSearch(HWND hwnd, int element_id,
                                  const unsigned char* search_bytes, int search_len);
void __stdcall EU_SetSelectOptionDisabled(HWND hwnd, int element_id, int option_index, int disabled);
int  __stdcall EU_GetSelectOptionCount(HWND hwnd, int element_id);
int  __stdcall EU_GetSelectMatchedCount(HWND hwnd, int element_id);
int  __stdcall EU_GetSelectOptionDisabled(HWND hwnd, int element_id, int option_index);
void __stdcall EU_SetSelectMultiple(HWND hwnd, int element_id, int multiple);
int  __stdcall EU_GetSelectMultiple(HWND hwnd, int element_id);
void __stdcall EU_SetSelectSelectedIndices(HWND hwnd, int element_id,
                                           const unsigned char* indices_bytes, int indices_len);
int  __stdcall EU_GetSelectSelectedCount(HWND hwnd, int element_id);
int  __stdcall EU_GetSelectSelectedAt(HWND hwnd, int element_id, int position);
void __stdcall EU_SetSelectChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetSelectV2Options(HWND hwnd, int element_id,
                                     const unsigned char* options_bytes, int options_len);
void __stdcall EU_SetSelectV2Index(HWND hwnd, int element_id, int index);
void __stdcall EU_SetSelectV2VisibleCount(HWND hwnd, int element_id, int visible_count);
int  __stdcall EU_GetSelectV2Index(HWND hwnd, int element_id);
int  __stdcall EU_GetSelectV2VisibleCount(HWND hwnd, int element_id);
void __stdcall EU_SetSelectV2Open(HWND hwnd, int element_id, int open);
int  __stdcall EU_GetSelectV2Open(HWND hwnd, int element_id);
void __stdcall EU_SetSelectV2Search(HWND hwnd, int element_id,
                                    const unsigned char* search_bytes, int search_len);
void __stdcall EU_SetSelectV2OptionDisabled(HWND hwnd, int element_id, int option_index, int disabled);
int  __stdcall EU_GetSelectV2OptionCount(HWND hwnd, int element_id);
int  __stdcall EU_GetSelectV2MatchedCount(HWND hwnd, int element_id);
int  __stdcall EU_GetSelectV2OptionDisabled(HWND hwnd, int element_id, int option_index);
void __stdcall EU_SetSelectV2ScrollIndex(HWND hwnd, int element_id, int scroll_index);
int  __stdcall EU_GetSelectV2ScrollIndex(HWND hwnd, int element_id);
void __stdcall EU_SetSelectV2ChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetRateValue(HWND hwnd, int element_id, int value);
int  __stdcall EU_GetRateValue(HWND hwnd, int element_id);
void __stdcall EU_SetRateMax(HWND hwnd, int element_id, int max_value);
int  __stdcall EU_GetRateMax(HWND hwnd, int element_id);
void __stdcall EU_SetRateValueX2(HWND hwnd, int element_id, int value_x2);
int  __stdcall EU_GetRateValueX2(HWND hwnd, int element_id);
void __stdcall EU_SetRateOptions(HWND hwnd, int element_id, int allow_clear, int allow_half, int readonly);
int  __stdcall EU_GetRateOptions(HWND hwnd, int element_id,
                                 int* allow_clear, int* allow_half, int* readonly, int* show_score);
void __stdcall EU_SetRateTexts(HWND hwnd, int element_id,
                               const unsigned char* low_bytes, int low_len,
                               const unsigned char* high_bytes, int high_len,
                               int show_score);
void __stdcall EU_SetRateColors(HWND hwnd, int element_id, Color low_color, Color mid_color, Color high_color);
int  __stdcall EU_GetRateColors(HWND hwnd, int element_id, Color* low_color, Color* mid_color, Color* high_color);
void __stdcall EU_SetRateIcons(HWND hwnd, int element_id,
                               const unsigned char* full_bytes, int full_len,
                               const unsigned char* void_bytes, int void_len,
                               const unsigned char* low_bytes, int low_len,
                               const unsigned char* mid_bytes, int mid_len,
                               const unsigned char* high_bytes, int high_len);
int  __stdcall EU_GetRateIcons(HWND hwnd, int element_id,
                               unsigned char* full_buffer, int full_buffer_size,
                               unsigned char* void_buffer, int void_buffer_size,
                               unsigned char* low_buffer, int low_buffer_size,
                               unsigned char* mid_buffer, int mid_buffer_size,
                               unsigned char* high_buffer, int high_buffer_size);
void __stdcall EU_SetRateTextItems(HWND hwnd, int element_id,
                                   const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetRateDisplayOptions(HWND hwnd, int element_id,
                                        int show_text, int show_score, Color text_color,
                                        const unsigned char* template_bytes, int template_len);
int  __stdcall EU_GetRateDisplayOptions(HWND hwnd, int element_id,
                                        int* show_text, int* show_score, Color* text_color,
                                        unsigned char* template_buffer, int template_buffer_size);
void __stdcall EU_SetRateChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetColorPickerColor(HWND hwnd, int element_id, Color color);
int  __stdcall EU_GetColorPickerColor(HWND hwnd, int element_id);
void __stdcall EU_SetColorPickerAlpha(HWND hwnd, int element_id, int alpha);
int  __stdcall EU_GetColorPickerAlpha(HWND hwnd, int element_id);
int  __stdcall EU_SetColorPickerHex(HWND hwnd, int element_id,
                                    const unsigned char* hex_bytes, int hex_len);
int  __stdcall EU_GetColorPickerHex(HWND hwnd, int element_id,
                                    unsigned char* buffer, int buffer_size);
void __stdcall EU_SetColorPickerOpen(HWND hwnd, int element_id, int open);
int  __stdcall EU_GetColorPickerOpen(HWND hwnd, int element_id);
void __stdcall EU_SetColorPickerPalette(HWND hwnd, int element_id,
                                        const Color* colors, int count);
int  __stdcall EU_GetColorPickerPaletteCount(HWND hwnd, int element_id);
void __stdcall EU_SetColorPickerChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetTagType(HWND hwnd, int element_id, int tag_type);
void __stdcall EU_SetTagEffect(HWND hwnd, int element_id, int effect);
void __stdcall EU_SetTagClosable(HWND hwnd, int element_id, int closable);
void __stdcall EU_SetTagClosed(HWND hwnd, int element_id, int closed);
int  __stdcall EU_GetTagClosed(HWND hwnd, int element_id);
int  __stdcall EU_GetTagOptions(HWND hwnd, int element_id,
                                int* tag_type, int* effect, int* closable, int* closed);
void __stdcall EU_SetTagSize(HWND hwnd, int element_id, int size_preset);
void __stdcall EU_SetTagThemeColor(HWND hwnd, int element_id, Color color);
int  __stdcall EU_GetTagVisualOptions(HWND hwnd, int element_id,
                                      int* size_preset, Color* theme_color);
void __stdcall EU_SetTagCloseCallback(HWND hwnd, int element_id, ElementClickCallback cb);
void __stdcall EU_SetBadgeValue(HWND hwnd, int element_id,
                                const unsigned char* value_bytes, int value_len);
void __stdcall EU_SetBadgeMax(HWND hwnd, int element_id, int max_value);
void __stdcall EU_SetBadgeType(HWND hwnd, int element_id, int badge_type);
void __stdcall EU_SetBadgeDot(HWND hwnd, int element_id, int dot);
void __stdcall EU_SetBadgeOptions(HWND hwnd, int element_id,
                                  int dot, int show_zero, int offset_x, int offset_y);
int  __stdcall EU_GetBadgeHidden(HWND hwnd, int element_id);
int  __stdcall EU_GetBadgeOptions(HWND hwnd, int element_id,
                                  int* max_value, int* dot, int* show_zero, int* offset_x, int* offset_y);
int  __stdcall EU_GetBadgeType(HWND hwnd, int element_id);
void __stdcall EU_SetBadgeLayoutOptions(HWND hwnd, int element_id,
                                        int placement, int standalone);
int  __stdcall EU_GetBadgeLayoutOptions(HWND hwnd, int element_id,
                                        int* placement, int* standalone);
void __stdcall EU_SetProgressPercentage(HWND hwnd, int element_id, int percentage);
int  __stdcall EU_GetProgressPercentage(HWND hwnd, int element_id);
void __stdcall EU_SetProgressStatus(HWND hwnd, int element_id, int status);
int  __stdcall EU_GetProgressStatus(HWND hwnd, int element_id);
void __stdcall EU_SetProgressShowText(HWND hwnd, int element_id, int show_text);
void __stdcall EU_SetProgressOptions(HWND hwnd, int element_id,
                                     int progress_type, int stroke_width, int show_text);
int  __stdcall EU_GetProgressOptions(HWND hwnd, int element_id,
                                     int* progress_type, int* stroke_width, int* show_text);
void __stdcall EU_SetProgressFormatOptions(HWND hwnd, int element_id,
                                           int text_format, int striped);
int  __stdcall EU_GetProgressFormatOptions(HWND hwnd, int element_id,
                                           int* text_format, int* striped);
void __stdcall EU_SetAvatarShape(HWND hwnd, int element_id, int shape);
void __stdcall EU_SetAvatarSource(HWND hwnd, int element_id,
                                  const unsigned char* src_bytes, int src_len);
void __stdcall EU_SetAvatarFit(HWND hwnd, int element_id, int fit);
int  __stdcall EU_GetAvatarImageStatus(HWND hwnd, int element_id);
int  __stdcall EU_GetAvatarOptions(HWND hwnd, int element_id, int* shape, int* fit);
void __stdcall EU_SetEmptyDescription(HWND hwnd, int element_id,
                                      const unsigned char* desc_bytes, int desc_len);
void __stdcall EU_SetEmptyOptions(HWND hwnd, int element_id,
                                  const unsigned char* icon_bytes, int icon_len,
                                  const unsigned char* action_bytes, int action_len);
void __stdcall EU_SetEmptyActionClicked(HWND hwnd, int element_id, int clicked);
int  __stdcall EU_GetEmptyActionClicked(HWND hwnd, int element_id);
void __stdcall EU_SetEmptyActionCallback(HWND hwnd, int element_id, ElementClickCallback cb);
void __stdcall EU_SetSkeletonRows(HWND hwnd, int element_id, int rows);
void __stdcall EU_SetSkeletonAnimated(HWND hwnd, int element_id, int animated);
void __stdcall EU_SetSkeletonLoading(HWND hwnd, int element_id, int loading);
void __stdcall EU_SetSkeletonOptions(HWND hwnd, int element_id,
                                     int rows, int animated, int loading, int show_avatar);
int  __stdcall EU_GetSkeletonLoading(HWND hwnd, int element_id);
int  __stdcall EU_GetSkeletonOptions(HWND hwnd, int element_id,
                                     int* rows, int* animated, int* loading, int* show_avatar);
void __stdcall EU_SetDescriptionsItems(HWND hwnd, int element_id,
                                       const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetDescriptionsColumns(HWND hwnd, int element_id, int columns);
void __stdcall EU_SetDescriptionsBordered(HWND hwnd, int element_id, int bordered);
void __stdcall EU_SetDescriptionsOptions(HWND hwnd, int element_id, int columns,
                                         int bordered, int label_width,
                                         int min_row_height, int wrap_values);
int  __stdcall EU_GetDescriptionsItemCount(HWND hwnd, int element_id);
void __stdcall EU_SetDescriptionsAdvancedOptions(HWND hwnd, int element_id,
                                                 int responsive, int last_item_span);
int  __stdcall EU_GetDescriptionsOptions(HWND hwnd, int element_id,
                                         int* columns, int* bordered,
                                         int* label_width, int* min_row_height,
                                         int* wrap_values, int* responsive,
                                         int* last_item_span);
void __stdcall EU_SetTableData(HWND hwnd, int element_id,
                               const unsigned char* columns_bytes, int columns_len,
                               const unsigned char* rows_bytes, int rows_len);
void __stdcall EU_SetTableStriped(HWND hwnd, int element_id, int striped);
void __stdcall EU_SetTableBordered(HWND hwnd, int element_id, int bordered);
void __stdcall EU_SetTableEmptyText(HWND hwnd, int element_id,
                                    const unsigned char* text_bytes, int text_len);
void __stdcall EU_SetTableSelectedRow(HWND hwnd, int element_id, int row_index);
int  __stdcall EU_GetTableSelectedRow(HWND hwnd, int element_id);
int  __stdcall EU_GetTableRowCount(HWND hwnd, int element_id);
int  __stdcall EU_GetTableColumnCount(HWND hwnd, int element_id);
void __stdcall EU_SetTableOptions(HWND hwnd, int element_id, int striped,
                                  int bordered, int row_height,
                                  int header_height, int selectable);
void __stdcall EU_SetTableSort(HWND hwnd, int element_id, int column_index, int desc);
void __stdcall EU_SetTableScrollRow(HWND hwnd, int element_id, int scroll_row);
void __stdcall EU_SetTableColumnWidth(HWND hwnd, int element_id, int column_width);
int  __stdcall EU_GetTableOptions(HWND hwnd, int element_id,
                                  int* striped, int* bordered,
                                  int* row_height, int* header_height,
                                  int* selectable, int* sort_column,
                                  int* sort_desc, int* scroll_row,
                                  int* column_width);
void __stdcall EU_SetTableColumnsEx(HWND hwnd, int element_id,
                                    const unsigned char* columns_bytes, int columns_len);
void __stdcall EU_SetTableRowsEx(HWND hwnd, int element_id,
                                 const unsigned char* rows_bytes, int rows_len);
void __stdcall EU_SetTableCellEx(HWND hwnd, int element_id, int row, int col, int type,
                                 const unsigned char* value_bytes, int value_len,
                                 const unsigned char* options_bytes, int options_len);
void __stdcall EU_SetTableRowStyle(HWND hwnd, int element_id, int row,
                                   unsigned int bg, unsigned int fg,
                                   int align, int font_flags, int font_size);
void __stdcall EU_SetTableCellStyle(HWND hwnd, int element_id, int row, int col,
                                    unsigned int bg, unsigned int fg,
                                    int align, int font_flags, int font_size);
void __stdcall EU_SetTableSelectionMode(HWND hwnd, int element_id, int mode);
void __stdcall EU_SetTableSelectedRows(HWND hwnd, int element_id,
                                       const unsigned char* rows_bytes, int rows_len);
void __stdcall EU_SetTableFilter(HWND hwnd, int element_id, int col,
                                 const unsigned char* value_bytes, int value_len);
void __stdcall EU_ClearTableFilter(HWND hwnd, int element_id, int col);
void __stdcall EU_SetTableSearch(HWND hwnd, int element_id,
                                 const unsigned char* value_bytes, int value_len);
void __stdcall EU_SetTableSpan(HWND hwnd, int element_id, int row, int col,
                               int rowspan, int colspan);
void __stdcall EU_ClearTableSpans(HWND hwnd, int element_id);
void __stdcall EU_SetTableSummary(HWND hwnd, int element_id,
                                  const unsigned char* values_bytes, int values_len);
void __stdcall EU_SetTableRowExpanded(HWND hwnd, int element_id, int row, int expanded);
void __stdcall EU_SetTableTreeOptions(HWND hwnd, int element_id, int enabled, int indent, int lazy);
void __stdcall EU_SetTableViewportOptions(HWND hwnd, int element_id, int max_height,
                                          int fixed_header, int horizontal_scroll,
                                          int show_summary);
void __stdcall EU_SetTableScroll(HWND hwnd, int element_id, int scroll_row, int scroll_x);
void __stdcall EU_SetTableHeaderDragOptions(HWND hwnd, int element_id, int column_resize,
                                            int header_height_resize, int min_col_width,
                                            int max_col_width, int min_header_height,
                                            int max_header_height);
int  __stdcall EU_ExportTableExcel(HWND hwnd, int element_id,
                                    const unsigned char* path_bytes, int path_len, int flags);
int  __stdcall EU_ImportTableExcel(HWND hwnd, int element_id,
                                    const unsigned char* path_bytes, int path_len, int flags);
void __stdcall EU_SetTableCellClickCallback(HWND hwnd, int element_id, TableCellCallback cb);
void __stdcall EU_SetTableCellActionCallback(HWND hwnd, int element_id, TableCellCallback cb);
void __stdcall EU_SetTableVirtualOptions(HWND hwnd, int element_id, int enabled,
                                         int row_count, int cache_window);
void __stdcall EU_SetTableVirtualRowProvider(HWND hwnd, int element_id, TableVirtualRowCallback cb);
void __stdcall EU_ClearTableVirtualCache(HWND hwnd, int element_id);
int  __stdcall EU_GetTableCellValue(HWND hwnd, int element_id, int row, int col,
                                    unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetTableFullState(HWND hwnd, int element_id,
                                    unsigned char* buffer, int buffer_size);
void __stdcall EU_SetCardBody(HWND hwnd, int element_id,
                              const unsigned char* body_bytes, int body_len);
void __stdcall EU_SetCardFooter(HWND hwnd, int element_id,
                                const unsigned char* footer_bytes, int footer_len);
void __stdcall EU_SetCardActions(HWND hwnd, int element_id,
                                 const unsigned char* actions_bytes, int actions_len);
int  __stdcall EU_GetCardAction(HWND hwnd, int element_id);
void __stdcall EU_ResetCardAction(HWND hwnd, int element_id);
void __stdcall EU_SetCardShadow(HWND hwnd, int element_id, int shadow);
void __stdcall EU_SetCardOptions(HWND hwnd, int element_id, int shadow, int hoverable);
int  __stdcall EU_GetCardOptions(HWND hwnd, int element_id,
                                 int* shadow, int* hoverable, int* action_count);
void __stdcall EU_SetCollapseItems(HWND hwnd, int element_id,
                                   const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetCollapseActive(HWND hwnd, int element_id, int active_index);
int  __stdcall EU_GetCollapseActive(HWND hwnd, int element_id);
int  __stdcall EU_GetCollapseItemCount(HWND hwnd, int element_id);
void __stdcall EU_SetCollapseOptions(HWND hwnd, int element_id, int accordion,
                                     int allow_collapse,
                                     const unsigned char* disabled_bytes,
                                     int disabled_len);
void __stdcall EU_SetCollapseAdvancedOptions(HWND hwnd, int element_id, int accordion,
                                             int allow_collapse, int animated,
                                             const unsigned char* disabled_bytes,
                                             int disabled_len);
int  __stdcall EU_GetCollapseOptions(HWND hwnd, int element_id,
                                     int* accordion, int* allow_collapse,
                                     int* animated, int* disabled_count);
void __stdcall EU_SetTimelineItems(HWND hwnd, int element_id,
                                   const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetTimelineOptions(HWND hwnd, int element_id, int position, int show_time);
int  __stdcall EU_GetTimelineItemCount(HWND hwnd, int element_id);
int  __stdcall EU_GetTimelineOptions(HWND hwnd, int element_id,
                                     int* position, int* show_time);
void __stdcall EU_SetTimelineAdvancedOptions(HWND hwnd, int element_id,
                                             int position, int show_time,
                                             int reverse, int default_placement);
int  __stdcall EU_GetTimelineAdvancedOptions(HWND hwnd, int element_id,
                                             int* position, int* show_time,
                                             int* reverse, int* default_placement);
void __stdcall EU_SetStatisticValue(HWND hwnd, int element_id,
                                     const unsigned char* value_bytes, int value_len);
void __stdcall EU_SetStatisticFormat(HWND hwnd, int element_id,
                                     const unsigned char* title_bytes, int title_len,
                                     const unsigned char* prefix_bytes, int prefix_len,
                                     const unsigned char* suffix_bytes, int suffix_len);
void __stdcall EU_SetStatisticOptions(HWND hwnd, int element_id,
                                      int precision, int animated);
int  __stdcall EU_GetStatisticOptions(HWND hwnd, int element_id,
                                      int* precision, int* animated);
void __stdcall EU_SetKpiCardData(HWND hwnd, int element_id,
                                 const unsigned char* value_bytes, int value_len,
                                 const unsigned char* subtitle_bytes, int subtitle_len,
                                 const unsigned char* trend_bytes, int trend_len,
                                 int trend_type);
void __stdcall EU_SetKpiCardOptions(HWND hwnd, int element_id, int loading,
                                    const unsigned char* helper_bytes, int helper_len);
int  __stdcall EU_GetKpiCardOptions(HWND hwnd, int element_id, int* loading, int* trend_type);
void __stdcall EU_SetTrendData(HWND hwnd, int element_id,
                               const unsigned char* value_bytes, int value_len,
                               const unsigned char* percent_bytes, int percent_len,
                               const unsigned char* detail_bytes, int detail_len,
                               int direction);
void __stdcall EU_SetTrendOptions(HWND hwnd, int element_id, int inverse, int show_icon);
int  __stdcall EU_GetTrendDirection(HWND hwnd, int element_id);
int  __stdcall EU_GetTrendOptions(HWND hwnd, int element_id, int* inverse, int* show_icon);
void __stdcall EU_SetStatusDot(HWND hwnd, int element_id,
                               const unsigned char* label_bytes, int label_len,
                               const unsigned char* desc_bytes, int desc_len,
                               int status);
void __stdcall EU_SetStatusDotOptions(HWND hwnd, int element_id, int pulse, int compact);
int  __stdcall EU_GetStatusDotStatus(HWND hwnd, int element_id);
int  __stdcall EU_GetStatusDotOptions(HWND hwnd, int element_id, int* pulse, int* compact);
void __stdcall EU_SetGaugeValue(HWND hwnd, int element_id, int value,
                                const unsigned char* caption_bytes, int caption_len,
                                int status);
void __stdcall EU_SetGaugeOptions(HWND hwnd, int element_id, int min_value, int max_value,
                                  int warning_value, int danger_value, int stroke_width);
int  __stdcall EU_GetGaugeValue(HWND hwnd, int element_id);
int  __stdcall EU_GetGaugeStatus(HWND hwnd, int element_id);
int  __stdcall EU_GetGaugeOptions(HWND hwnd, int element_id, int* min_value, int* max_value,
                                  int* warning_value, int* danger_value, int* stroke_width);
void __stdcall EU_SetRingProgressValue(HWND hwnd, int element_id, int value,
                                       const unsigned char* label_bytes, int label_len,
                                       int status);
void __stdcall EU_SetRingProgressOptions(HWND hwnd, int element_id,
                                         int stroke_width, int show_center);
int  __stdcall EU_GetRingProgressValue(HWND hwnd, int element_id);
int  __stdcall EU_GetRingProgressStatus(HWND hwnd, int element_id);
int  __stdcall EU_GetRingProgressOptions(HWND hwnd, int element_id,
                                         int* stroke_width, int* show_center);
void __stdcall EU_SetBulletProgressValue(HWND hwnd, int element_id,
                                         int value, int target,
                                         const unsigned char* desc_bytes, int desc_len,
                                         int status);
void __stdcall EU_SetBulletProgressOptions(HWND hwnd, int element_id,
                                           int good_threshold, int warn_threshold,
                                           int show_target);
int  __stdcall EU_GetBulletProgressValue(HWND hwnd, int element_id);
int  __stdcall EU_GetBulletProgressTarget(HWND hwnd, int element_id);
int  __stdcall EU_GetBulletProgressStatus(HWND hwnd, int element_id);
int  __stdcall EU_GetBulletProgressOptions(HWND hwnd, int element_id,
                                           int* good_threshold, int* warn_threshold,
                                           int* show_target);
void __stdcall EU_SetLineChartData(HWND hwnd, int element_id,
                                   const unsigned char* points_bytes, int points_len);
void __stdcall EU_SetLineChartSeries(HWND hwnd, int element_id,
                                     const unsigned char* series_bytes, int series_len);
void __stdcall EU_SetLineChartOptions(HWND hwnd, int element_id,
                                      int chart_style, int show_axis,
                                      int show_area, int show_tooltip);
void __stdcall EU_SetLineChartSelected(HWND hwnd, int element_id, int selected_index);
int  __stdcall EU_GetLineChartPointCount(HWND hwnd, int element_id);
int  __stdcall EU_GetLineChartSeriesCount(HWND hwnd, int element_id);
int  __stdcall EU_GetLineChartSelected(HWND hwnd, int element_id);
int  __stdcall EU_GetLineChartOptions(HWND hwnd, int element_id,
                                      int* chart_style, int* show_axis,
                                      int* show_area, int* show_tooltip);
void __stdcall EU_SetBarChartData(HWND hwnd, int element_id,
                                  const unsigned char* bars_bytes, int bars_len);
void __stdcall EU_SetBarChartSeries(HWND hwnd, int element_id,
                                    const unsigned char* series_bytes, int series_len);
void __stdcall EU_SetBarChartOptions(HWND hwnd, int element_id,
                                     int orientation, int show_values, int show_axis);
void __stdcall EU_SetBarChartSelected(HWND hwnd, int element_id, int selected_index);
int  __stdcall EU_GetBarChartBarCount(HWND hwnd, int element_id);
int  __stdcall EU_GetBarChartSeriesCount(HWND hwnd, int element_id);
int  __stdcall EU_GetBarChartSelected(HWND hwnd, int element_id);
int  __stdcall EU_GetBarChartOptions(HWND hwnd, int element_id,
                                     int* orientation, int* show_values, int* show_axis);
void __stdcall EU_SetDonutChartData(HWND hwnd, int element_id,
                                    const unsigned char* slices_bytes, int slices_len,
                                    int active_index);
void __stdcall EU_SetDonutChartOptions(HWND hwnd, int element_id,
                                       int show_legend, int ring_width);
void __stdcall EU_SetDonutChartAdvancedOptions(HWND hwnd, int element_id,
                                               int show_legend, int ring_width,
                                               int show_labels);
void __stdcall EU_SetDonutChartActive(HWND hwnd, int element_id, int active_index);
int  __stdcall EU_GetDonutChartSliceCount(HWND hwnd, int element_id);
int  __stdcall EU_GetDonutChartActive(HWND hwnd, int element_id);
int  __stdcall EU_GetDonutChartOptions(HWND hwnd, int element_id,
                                       int* show_legend, int* ring_width);
int  __stdcall EU_GetDonutChartAdvancedOptions(HWND hwnd, int element_id,
                                               int* show_legend, int* ring_width,
                                               int* show_labels);
void __stdcall EU_SetCalendarDate(HWND hwnd, int element_id, int year, int month, int selected_day);
void __stdcall EU_SetCalendarRange(HWND hwnd, int element_id, int min_yyyymmdd, int max_yyyymmdd);
void __stdcall EU_SetCalendarOptions(HWND hwnd, int element_id, int today_yyyymmdd, int show_today);
void __stdcall EU_CalendarMoveMonth(HWND hwnd, int element_id, int delta_months);
int  __stdcall EU_GetCalendarValue(HWND hwnd, int element_id);
int  __stdcall EU_GetCalendarRange(HWND hwnd, int element_id, int* min_yyyymmdd, int* max_yyyymmdd);
int  __stdcall EU_GetCalendarOptions(HWND hwnd, int element_id, int* today_yyyymmdd, int* show_today);
void __stdcall EU_SetCalendarSelectionRange(HWND hwnd, int element_id,
                                             int start_yyyymmdd, int end_yyyymmdd,
                                             int enabled);
int  __stdcall EU_GetCalendarSelectionRange(HWND hwnd, int element_id,
                                             int* start_yyyymmdd, int* end_yyyymmdd,
                                             int* enabled);
void __stdcall EU_SetCalendarDisplayRange(HWND hwnd, int element_id, int start_yyyymmdd, int end_yyyymmdd);
int  __stdcall EU_GetCalendarDisplayRange(HWND hwnd, int element_id, int* start_yyyymmdd, int* end_yyyymmdd);
void __stdcall EU_SetCalendarCellItems(HWND hwnd, int element_id, const unsigned char* spec_bytes, int spec_len);
int  __stdcall EU_GetCalendarCellItems(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size);
void __stdcall EU_ClearCalendarCellItems(HWND hwnd, int element_id);
void __stdcall EU_SetCalendarVisualOptions(HWND hwnd, int element_id,
                                           int show_header, int show_week_header,
                                           int label_mode, int show_adjacent_days,
                                           float cell_radius);
int  __stdcall EU_GetCalendarVisualOptions(HWND hwnd, int element_id,
                                           int* show_header, int* show_week_header,
                                           int* label_mode, int* show_adjacent_days,
                                           float* cell_radius);
void __stdcall EU_SetCalendarStateColors(HWND hwnd, int element_id,
                                          Color selected_bg, Color selected_fg,
                                          Color range_bg, Color today_border,
                                          Color hover_bg, Color disabled_fg,
                                          Color adjacent_fg);
int  __stdcall EU_GetCalendarStateColors(HWND hwnd, int element_id,
                                          Color* selected_bg, Color* selected_fg,
                                          Color* range_bg, Color* today_border,
                                          Color* hover_bg, Color* disabled_fg,
                                          Color* adjacent_fg);
void __stdcall EU_SetCalendarSelectedMarker(HWND hwnd, int element_id,
                                            const unsigned char* marker_bytes, int marker_len);
void __stdcall EU_SetCalendarChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetTreeItems(HWND hwnd, int element_id,
                               const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetTreeSelected(HWND hwnd, int element_id, int selected_index);
int  __stdcall EU_GetTreeSelected(HWND hwnd, int element_id);
void __stdcall EU_SetTreeOptions(HWND hwnd, int element_id,
                                 int show_checkbox, int keyboard_navigation, int lazy_mode);
int  __stdcall EU_GetTreeOptions(HWND hwnd, int element_id,
                                 int* show_checkbox, int* keyboard_navigation,
                                 int* lazy_mode, int* checked_count, int* last_lazy_index);
void __stdcall EU_SetTreeItemExpanded(HWND hwnd, int element_id, int item_index, int expanded);
void __stdcall EU_ToggleTreeItemExpanded(HWND hwnd, int element_id, int item_index);
int  __stdcall EU_GetTreeItemExpanded(HWND hwnd, int element_id, int item_index);
void __stdcall EU_SetTreeItemChecked(HWND hwnd, int element_id, int item_index, int checked);
int  __stdcall EU_GetTreeItemChecked(HWND hwnd, int element_id, int item_index);
void __stdcall EU_SetTreeItemLazy(HWND hwnd, int element_id, int item_index, int lazy);
int  __stdcall EU_GetTreeItemLazy(HWND hwnd, int element_id, int item_index);
int  __stdcall EU_GetTreeVisibleCount(HWND hwnd, int element_id);
void __stdcall EU_SetTreeSelectItems(HWND hwnd, int element_id,
                                     const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetTreeSelectSelected(HWND hwnd, int element_id, int selected_index);
int  __stdcall EU_GetTreeSelectSelected(HWND hwnd, int element_id);
void __stdcall EU_SetTreeSelectOpen(HWND hwnd, int element_id, int open);
int  __stdcall EU_GetTreeSelectOpen(HWND hwnd, int element_id);
void __stdcall EU_SetTreeSelectOptions(HWND hwnd, int element_id,
                                       int multiple, int clearable, int searchable);
int  __stdcall EU_GetTreeSelectOptions(HWND hwnd, int element_id,
                                       int* multiple, int* clearable, int* searchable,
                                       int* selected_count, int* matched_count);
void __stdcall EU_SetTreeSelectSearch(HWND hwnd, int element_id,
                                      const unsigned char* search_bytes, int search_len);
int  __stdcall EU_GetTreeSelectSearch(HWND hwnd, int element_id,
                                      unsigned char* buffer, int buffer_size);
void __stdcall EU_ClearTreeSelect(HWND hwnd, int element_id);
void __stdcall EU_SetTreeSelectSelectedItems(HWND hwnd, int element_id,
                                             const unsigned char* indices_bytes, int indices_len);
int  __stdcall EU_GetTreeSelectSelectedCount(HWND hwnd, int element_id);
int  __stdcall EU_GetTreeSelectSelectedItem(HWND hwnd, int element_id, int position);
void __stdcall EU_SetTreeSelectItemExpanded(HWND hwnd, int element_id, int item_index, int expanded);
void __stdcall EU_ToggleTreeSelectItemExpanded(HWND hwnd, int element_id, int item_index);
int  __stdcall EU_GetTreeSelectItemExpanded(HWND hwnd, int element_id, int item_index);
void __stdcall EU_SetTreeDataJson(HWND hwnd, int element_id,
                                  const unsigned char* json_bytes, int json_len);
int  __stdcall EU_GetTreeDataJson(HWND hwnd, int element_id,
                                  unsigned char* buffer, int buffer_size);
void __stdcall EU_SetTreeOptionsJson(HWND hwnd, int element_id,
                                     const unsigned char* json_bytes, int json_len);
int  __stdcall EU_GetTreeStateJson(HWND hwnd, int element_id,
                                   unsigned char* buffer, int buffer_size);
void __stdcall EU_SetTreeCheckedKeysJson(HWND hwnd, int element_id,
                                         const unsigned char* json_bytes, int json_len);
int  __stdcall EU_GetTreeCheckedKeysJson(HWND hwnd, int element_id,
                                         unsigned char* buffer, int buffer_size);
void __stdcall EU_SetTreeExpandedKeysJson(HWND hwnd, int element_id,
                                          const unsigned char* json_bytes, int json_len);
int  __stdcall EU_GetTreeExpandedKeysJson(HWND hwnd, int element_id,
                                          unsigned char* buffer, int buffer_size);
void __stdcall EU_AppendTreeNodeJson(HWND hwnd, int element_id,
                                     const unsigned char* parent_key_bytes, int parent_key_len,
                                     const unsigned char* json_bytes, int json_len);
void __stdcall EU_UpdateTreeNodeJson(HWND hwnd, int element_id,
                                     const unsigned char* key_bytes, int key_len,
                                     const unsigned char* json_bytes, int json_len);
void __stdcall EU_RemoveTreeNodeByKey(HWND hwnd, int element_id,
                                      const unsigned char* key_bytes, int key_len);
void __stdcall EU_SetTreeNodeEventCallback(HWND hwnd, int element_id, TreeNodeEventCallback cb);
void __stdcall EU_SetTreeLazyLoadCallback(HWND hwnd, int element_id, TreeNodeEventCallback cb);
void __stdcall EU_SetTreeDragCallback(HWND hwnd, int element_id, TreeNodeEventCallback cb);
void __stdcall EU_SetTreeAllowDragCallback(HWND hwnd, int element_id, TreeNodeAllowDragCallback cb);
void __stdcall EU_SetTreeAllowDropCallback(HWND hwnd, int element_id, TreeNodeAllowDropCallback cb);
void __stdcall EU_SetTreeSelectDataJson(HWND hwnd, int element_id,
                                        const unsigned char* json_bytes, int json_len);
int  __stdcall EU_GetTreeSelectDataJson(HWND hwnd, int element_id,
                                        unsigned char* buffer, int buffer_size);
void __stdcall EU_SetTreeSelectOptionsJson(HWND hwnd, int element_id,
                                           const unsigned char* json_bytes, int json_len);
int  __stdcall EU_GetTreeSelectStateJson(HWND hwnd, int element_id,
                                         unsigned char* buffer, int buffer_size);
void __stdcall EU_SetTreeSelectSelectedKeysJson(HWND hwnd, int element_id,
                                                const unsigned char* json_bytes, int json_len);
int  __stdcall EU_GetTreeSelectSelectedKeysJson(HWND hwnd, int element_id,
                                                unsigned char* buffer, int buffer_size);
void __stdcall EU_SetTreeSelectExpandedKeysJson(HWND hwnd, int element_id,
                                                const unsigned char* json_bytes, int json_len);
int  __stdcall EU_GetTreeSelectExpandedKeysJson(HWND hwnd, int element_id,
                                                unsigned char* buffer, int buffer_size);
void __stdcall EU_AppendTreeSelectNodeJson(HWND hwnd, int element_id,
                                           const unsigned char* parent_key_bytes, int parent_key_len,
                                           const unsigned char* json_bytes, int json_len);
void __stdcall EU_UpdateTreeSelectNodeJson(HWND hwnd, int element_id,
                                           const unsigned char* key_bytes, int key_len,
                                           const unsigned char* json_bytes, int json_len);
void __stdcall EU_RemoveTreeSelectNodeByKey(HWND hwnd, int element_id,
                                            const unsigned char* key_bytes, int key_len);
void __stdcall EU_SetTreeSelectNodeEventCallback(HWND hwnd, int element_id, TreeNodeEventCallback cb);
void __stdcall EU_SetTreeSelectLazyLoadCallback(HWND hwnd, int element_id, TreeNodeEventCallback cb);
void __stdcall EU_SetTreeSelectDragCallback(HWND hwnd, int element_id, TreeNodeEventCallback cb);
void __stdcall EU_SetTreeSelectAllowDragCallback(HWND hwnd, int element_id, TreeNodeAllowDragCallback cb);
void __stdcall EU_SetTreeSelectAllowDropCallback(HWND hwnd, int element_id, TreeNodeAllowDropCallback cb);
void __stdcall EU_SetTransferItems(HWND hwnd, int element_id,
                                   const unsigned char* left_bytes, int left_len,
                                   const unsigned char* right_bytes, int right_len);
void __stdcall EU_TransferMoveRight(HWND hwnd, int element_id);
void __stdcall EU_TransferMoveLeft(HWND hwnd, int element_id);
void __stdcall EU_TransferMoveAllRight(HWND hwnd, int element_id);
void __stdcall EU_TransferMoveAllLeft(HWND hwnd, int element_id);
void __stdcall EU_SetTransferSelected(HWND hwnd, int element_id, int side, int selected_index);
int  __stdcall EU_GetTransferSelected(HWND hwnd, int element_id, int side);
int  __stdcall EU_GetTransferCount(HWND hwnd, int element_id, int side);
void __stdcall EU_SetTransferFilters(HWND hwnd, int element_id,
                                     const unsigned char* left_bytes, int left_len,
                                     const unsigned char* right_bytes, int right_len);
int  __stdcall EU_GetTransferMatchedCount(HWND hwnd, int element_id, int side);
void __stdcall EU_SetTransferItemDisabled(HWND hwnd, int element_id,
                                          int side, int item_index, int disabled);
int  __stdcall EU_GetTransferItemDisabled(HWND hwnd, int element_id,
                                          int side, int item_index);
int  __stdcall EU_GetTransferDisabledCount(HWND hwnd, int element_id, int side);
void __stdcall EU_SetTransferDataEx(HWND hwnd, int element_id,
                                    const unsigned char* items_bytes, int items_len,
                                    const unsigned char* target_bytes, int target_len);
void __stdcall EU_SetTransferOptions(HWND hwnd, int element_id,
                                     int filterable, int multiple, int show_footer,
                                     int show_select_all, int show_count, int render_mode);
int  __stdcall EU_GetTransferOptions(HWND hwnd, int element_id,
                                     int* filterable, int* multiple, int* show_footer,
                                     int* show_select_all, int* show_count, int* render_mode);
void __stdcall EU_SetTransferTitles(HWND hwnd, int element_id,
                                    const unsigned char* left_bytes, int left_len,
                                    const unsigned char* right_bytes, int right_len);
void __stdcall EU_SetTransferButtonTexts(HWND hwnd, int element_id,
                                         const unsigned char* left_bytes, int left_len,
                                         const unsigned char* right_bytes, int right_len);
void __stdcall EU_SetTransferFormat(HWND hwnd, int element_id,
                                    const unsigned char* no_checked_bytes, int no_checked_len,
                                    const unsigned char* has_checked_bytes, int has_checked_len);
void __stdcall EU_SetTransferItemTemplate(HWND hwnd, int element_id,
                                          const unsigned char* template_bytes, int template_len);
void __stdcall EU_SetTransferFooterTexts(HWND hwnd, int element_id,
                                         const unsigned char* left_bytes, int left_len,
                                         const unsigned char* right_bytes, int right_len);
void __stdcall EU_SetTransferFilterPlaceholder(HWND hwnd, int element_id,
                                               const unsigned char* text_bytes, int text_len);
void __stdcall EU_SetTransferCheckedKeys(HWND hwnd, int element_id,
                                         const unsigned char* left_bytes, int left_len,
                                         const unsigned char* right_bytes, int right_len);
int  __stdcall EU_GetTransferCheckedCount(HWND hwnd, int element_id, int side);
int  __stdcall EU_GetTransferValueKeys(HWND hwnd, int element_id,
                                      unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetTransferText(HWND hwnd, int element_id, int text_type,
                                 unsigned char* buffer, int buffer_size);
void __stdcall EU_SetAutocompleteSuggestions(HWND hwnd, int element_id,
                                             const unsigned char* suggestions_bytes, int suggestions_len);
void __stdcall EU_SetAutocompleteValue(HWND hwnd, int element_id,
                                       const unsigned char* value_bytes, int value_len);
void __stdcall EU_SetAutocompleteOpen(HWND hwnd, int element_id, int open);
void __stdcall EU_SetAutocompleteSelected(HWND hwnd, int element_id, int selected_index);
void __stdcall EU_SetAutocompleteAsyncState(HWND hwnd, int element_id, int loading, int request_id);
void __stdcall EU_SetAutocompleteEmptyText(HWND hwnd, int element_id,
                                           const unsigned char* text_bytes, int text_len);
void __stdcall EU_SetAutocompletePlaceholder(HWND hwnd, int element_id,
                                             const unsigned char* text_bytes, int text_len);
int  __stdcall EU_GetAutocompletePlaceholder(HWND hwnd, int element_id,
                                             unsigned char* buffer, int buffer_size);
void __stdcall EU_SetAutocompleteIcons(HWND hwnd, int element_id,
                                       const unsigned char* prefix_icon_bytes, int prefix_icon_len,
                                       const unsigned char* suffix_icon_bytes, int suffix_icon_len);
int  __stdcall EU_GetAutocompleteIcons(HWND hwnd, int element_id,
                                       unsigned char* prefix_icon_buffer, int prefix_icon_buffer_size,
                                       unsigned char* suffix_icon_buffer, int suffix_icon_buffer_size);
void __stdcall EU_SetAutocompleteBehaviorOptions(HWND hwnd, int element_id, int trigger_on_focus);
int  __stdcall EU_GetAutocompleteBehaviorOptions(HWND hwnd, int element_id, int* trigger_on_focus);
int  __stdcall EU_GetAutocompleteValue(HWND hwnd, int element_id,
                                       unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetAutocompleteOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetAutocompleteSelected(HWND hwnd, int element_id);
int  __stdcall EU_GetAutocompleteSuggestionCount(HWND hwnd, int element_id);
int  __stdcall EU_GetAutocompleteOptions(HWND hwnd, int element_id,
                                        int* open, int* selected_index,
                                        int* suggestion_count, int* loading,
                                        int* request_id);
void __stdcall EU_SetMentionsValue(HWND hwnd, int element_id,
                                   const unsigned char* value_bytes, int value_len);
void __stdcall EU_SetMentionsSuggestions(HWND hwnd, int element_id,
                                         const unsigned char* suggestions_bytes, int suggestions_len);
void __stdcall EU_SetMentionsOpen(HWND hwnd, int element_id, int open);
void __stdcall EU_SetMentionsSelected(HWND hwnd, int element_id, int selected_index);
void __stdcall EU_SetMentionsOptions(HWND hwnd, int element_id,
                                     const unsigned char* trigger_bytes, int trigger_len,
                                     int filter_enabled, int insert_space);
void __stdcall EU_SetMentionsFilter(HWND hwnd, int element_id,
                                    const unsigned char* filter_bytes, int filter_len);
void __stdcall EU_InsertMentionsSelected(HWND hwnd, int element_id);
int  __stdcall EU_GetMentionsValue(HWND hwnd, int element_id,
                                   unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetMentionsOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetMentionsSelected(HWND hwnd, int element_id);
int  __stdcall EU_GetMentionsSuggestionCount(HWND hwnd, int element_id);
int  __stdcall EU_GetMentionsOptions(HWND hwnd, int element_id,
                                    int* open, int* selected_index,
                                    int* suggestion_count, int* matched_count,
                                    int* trigger_code);
void __stdcall EU_SetCascaderOptions(HWND hwnd, int element_id,
                                     const unsigned char* options_bytes, int options_len);
void __stdcall EU_SetCascaderValue(HWND hwnd, int element_id,
                                   const unsigned char* selected_bytes, int selected_len);
void __stdcall EU_SetCascaderOpen(HWND hwnd, int element_id, int open);
void __stdcall EU_SetCascaderAdvancedOptions(HWND hwnd, int element_id,
                                             int searchable, int lazy_mode);
void __stdcall EU_SetCascaderSearch(HWND hwnd, int element_id,
                                    const unsigned char* search_bytes, int search_len);
int  __stdcall EU_GetCascaderOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetCascaderOptionCount(HWND hwnd, int element_id);
int  __stdcall EU_GetCascaderSelectedDepth(HWND hwnd, int element_id);
int  __stdcall EU_GetCascaderLevelCount(HWND hwnd, int element_id);
int  __stdcall EU_GetCascaderAdvancedOptions(HWND hwnd, int element_id,
                                            int* searchable, int* lazy_mode,
                                            int* matched_count, int* last_lazy_level);
void __stdcall EU_SetDatePickerDate(HWND hwnd, int element_id, int year, int month, int selected_day);
void __stdcall EU_SetDatePickerRange(HWND hwnd, int element_id, int min_yyyymmdd, int max_yyyymmdd);
void __stdcall EU_SetDatePickerOptions(HWND hwnd, int element_id, int today_yyyymmdd, int show_today, int date_format);
void __stdcall EU_SetDatePickerOpen(HWND hwnd, int element_id, int open);
void __stdcall EU_ClearDatePicker(HWND hwnd, int element_id);
void __stdcall EU_DatePickerSelectToday(HWND hwnd, int element_id);
int  __stdcall EU_GetDatePickerOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetDatePickerValue(HWND hwnd, int element_id);
void __stdcall EU_DatePickerMoveMonth(HWND hwnd, int element_id, int delta_months);
int  __stdcall EU_GetDatePickerRange(HWND hwnd, int element_id, int* min_yyyymmdd, int* max_yyyymmdd);
int  __stdcall EU_GetDatePickerOptions(HWND hwnd, int element_id,
                                       int* today_yyyymmdd, int* show_today, int* date_format);
void __stdcall EU_SetDatePickerSelectionRange(HWND hwnd, int element_id,
                                              int start_yyyymmdd, int end_yyyymmdd,
                                              int enabled);
int  __stdcall EU_GetDatePickerSelectionRange(HWND hwnd, int element_id,
                                              int* start_yyyymmdd, int* end_yyyymmdd,
                                              int* enabled);
void __stdcall EU_SetDatePickerPlaceholder(HWND hwnd, int element_id,
                                            const unsigned char* text_bytes, int text_len);
void __stdcall EU_SetDatePickerRangeSeparator(HWND hwnd, int element_id,
                                               const unsigned char* sep_bytes, int sep_len);
void __stdcall EU_SetDatePickerStartPlaceholder(HWND hwnd, int element_id,
                                                 const unsigned char* text_bytes, int text_len);
void __stdcall EU_SetDatePickerEndPlaceholder(HWND hwnd, int element_id,
                                               const unsigned char* text_bytes, int text_len);
void __stdcall EU_SetDatePickerFormat(HWND hwnd, int element_id,
                                       const unsigned char* fmt_bytes, int fmt_len);
void __stdcall EU_SetDatePickerAlign(HWND hwnd, int element_id, int align);
void __stdcall EU_SetDatePickerMode(HWND hwnd, int element_id, int mode);
int  __stdcall EU_GetDatePickerMode(HWND hwnd, int element_id);
void __stdcall EU_SetDatePickerMultiSelect(HWND hwnd, int element_id, int enabled);
int  __stdcall EU_GetDatePickerSelectedDates(HWND hwnd, int element_id, unsigned char* buffer, int buf_size);
void __stdcall EU_SetDatePickerShortcuts(HWND hwnd, int element_id,
                                          const unsigned char* shortcuts_bytes, int shortcuts_len);
void __stdcall EU_SetDatePickerDisabledDateCallback(HWND hwnd, int element_id,
                                                     int (*cb)(int id, int yyyymmdd));
int  __stdcall EU_CreateDateRangePicker(HWND hwnd, int parent_id,
                                         int start_yyyymmdd, int end_yyyymmdd,
                                         int x, int y, int w, int h);
void __stdcall EU_SetDateRangePickerValue(HWND hwnd, int element_id, int start, int end);
int  __stdcall EU_GetDateRangePickerValue(HWND hwnd, int element_id, int* start, int* end);
void __stdcall EU_SetDateRangePickerRange(HWND hwnd, int element_id, int min, int max);
void __stdcall EU_SetDateRangePickerPlaceholders(HWND hwnd, int element_id,
                                                  const unsigned char* start_bytes, int start_len,
                                                  const unsigned char* end_bytes, int end_len);
void __stdcall EU_SetDateRangePickerSeparator(HWND hwnd, int element_id,
                                               const unsigned char* sep_bytes, int sep_len);
void __stdcall EU_SetDateRangePickerFormat(HWND hwnd, int element_id, int fmt);
void __stdcall EU_SetDateRangePickerAlign(HWND hwnd, int element_id, int align);
void __stdcall EU_SetDateRangePickerShortcuts(HWND hwnd, int element_id,
                                               const unsigned char* sc_bytes, int sc_len);
void __stdcall EU_SetDateRangePickerDisabledDateCallback(HWND hwnd, int element_id,
                                                          int (*cb)(int id, int yyyymmdd));
void __stdcall EU_SetDateRangePickerOpen(HWND hwnd, int element_id, int open);
int  __stdcall EU_GetDateRangePickerOpen(HWND hwnd, int element_id);
void __stdcall EU_DateRangePickerClear(HWND hwnd, int element_id);

void __stdcall EU_SetTimePickerTime(HWND hwnd, int element_id, int hour, int minute);
void __stdcall EU_SetTimePickerRange(HWND hwnd, int element_id, int min_hhmm, int max_hhmm);
void __stdcall EU_SetTimePickerOptions(HWND hwnd, int element_id, int step_minutes, int time_format);
void __stdcall EU_SetTimePickerOpen(HWND hwnd, int element_id, int open);
void __stdcall EU_SetTimePickerScroll(HWND hwnd, int element_id, int hour_scroll, int minute_scroll);
int  __stdcall EU_GetTimePickerOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetTimePickerValue(HWND hwnd, int element_id);
int  __stdcall EU_GetTimePickerRange(HWND hwnd, int element_id, int* min_hhmm, int* max_hhmm);
int  __stdcall EU_GetTimePickerOptions(HWND hwnd, int element_id, int* step_minutes, int* time_format);
int  __stdcall EU_GetTimePickerScroll(HWND hwnd, int element_id, int* hour_scroll, int* minute_scroll);
void __stdcall EU_SetTimePickerArrowControl(HWND hwnd, int element_id, int enabled);
int  __stdcall EU_GetTimePickerArrowControl(HWND hwnd, int element_id);
void __stdcall EU_SetTimePickerRangeSelect(HWND hwnd, int element_id, int enabled,
                                            int start_hhmm, int end_hhmm);
void __stdcall EU_SetTimePickerStartPlaceholder(HWND hwnd, int element_id,
                                                 const unsigned char* text_bytes, int text_len);
void __stdcall EU_SetTimePickerEndPlaceholder(HWND hwnd, int element_id,
                                               const unsigned char* text_bytes, int text_len);
void __stdcall EU_SetTimePickerRangeSeparator(HWND hwnd, int element_id,
                                               const unsigned char* sep_bytes, int sep_len);
int  __stdcall EU_GetTimePickerRangeValue(HWND hwnd, int element_id,
                                           int* start_hhmm, int* end_hhmm, int* enabled);
void __stdcall EU_SetTimeSelectPlaceholder(HWND hwnd, int element_id,
                                            const unsigned char* text_bytes, int text_len);
void __stdcall EU_SetDateTimePickerDateTime(HWND hwnd, int element_id,
                                            int year, int month, int day,
                                            int hour, int minute);
void __stdcall EU_SetDateTimePickerRange(HWND hwnd, int element_id,
                                         int min_yyyymmdd, int max_yyyymmdd,
                                         int min_hhmm, int max_hhmm);
void __stdcall EU_SetDateTimePickerOptions(HWND hwnd, int element_id,
                                           int today_yyyymmdd, int show_today,
                                           int minute_step, int date_format);
void __stdcall EU_SetDateTimePickerOpen(HWND hwnd, int element_id, int open);
void __stdcall EU_ClearDateTimePicker(HWND hwnd, int element_id);
void __stdcall EU_DateTimePickerSelectToday(HWND hwnd, int element_id);
void __stdcall EU_DateTimePickerSelectNow(HWND hwnd, int element_id);
void __stdcall EU_SetDateTimePickerScroll(HWND hwnd, int element_id, int hour_scroll, int minute_scroll);
int  __stdcall EU_GetDateTimePickerOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetDateTimePickerDateValue(HWND hwnd, int element_id);
int  __stdcall EU_GetDateTimePickerTimeValue(HWND hwnd, int element_id);
void __stdcall EU_DateTimePickerMoveMonth(HWND hwnd, int element_id, int delta_months);
int  __stdcall EU_GetDateTimePickerRange(HWND hwnd, int element_id,
                                         int* min_yyyymmdd, int* max_yyyymmdd,
                                         int* min_hhmm, int* max_hhmm);
int  __stdcall EU_GetDateTimePickerOptions(HWND hwnd, int element_id,
                                           int* today_yyyymmdd, int* show_today,
                                           int* minute_step, int* date_format);
int  __stdcall EU_GetDateTimePickerScroll(HWND hwnd, int element_id,
                                          int* hour_scroll, int* minute_scroll);
void __stdcall EU_SetDateTimePickerShortcuts(HWND hwnd, int element_id,
                                              const unsigned char* shortcuts_bytes, int shortcuts_len);
void __stdcall EU_SetDateTimePickerStartPlaceholder(HWND hwnd, int element_id,
                                                     const unsigned char* text_bytes, int text_len);
void __stdcall EU_SetDateTimePickerEndPlaceholder(HWND hwnd, int element_id,
                                                   const unsigned char* text_bytes, int text_len);
void __stdcall EU_SetDateTimePickerDefaultTime(HWND hwnd, int element_id, int hour, int minute);
void __stdcall EU_SetDateTimePickerRangeDefaultTime(HWND hwnd, int element_id,
                                                     int start_hour, int start_minute,
                                                     int end_hour, int end_minute);
void __stdcall EU_SetDateTimePickerRangeSeparator(HWND hwnd, int element_id,
                                                   const unsigned char* sep_bytes, int sep_len);
void __stdcall EU_SetDateTimePickerRangeSelect(HWND hwnd, int element_id, int enabled,
                                                int start_date, int start_time,
                                                int end_date, int end_time);
int  __stdcall EU_GetDateTimePickerRangeValue(HWND hwnd, int element_id,
                                               int* start_date, int* start_time,
                                               int* end_date, int* end_time, int* enabled);
void __stdcall EU_SetTimeSelectTime(HWND hwnd, int element_id, int hour, int minute);
void __stdcall EU_SetTimeSelectRange(HWND hwnd, int element_id, int min_hhmm, int max_hhmm);
void __stdcall EU_SetTimeSelectOptions(HWND hwnd, int element_id, int step_minutes, int time_format);
void __stdcall EU_SetTimeSelectOpen(HWND hwnd, int element_id, int open);
void __stdcall EU_SetTimeSelectScroll(HWND hwnd, int element_id, int scroll_row);
int  __stdcall EU_GetTimeSelectOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetTimeSelectValue(HWND hwnd, int element_id);
int  __stdcall EU_GetTimeSelectRange(HWND hwnd, int element_id, int* min_hhmm, int* max_hhmm);
int  __stdcall EU_GetTimeSelectOptions(HWND hwnd, int element_id, int* step_minutes, int* time_format);
int  __stdcall EU_GetTimeSelectState(HWND hwnd, int element_id,
                                     int* scroll_row, int* candidate_count,
                                     int* group_count, int* active_index);
void __stdcall EU_SetDropdownItems(HWND hwnd, int element_id,
                                   const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetDropdownSelected(HWND hwnd, int element_id, int selected_index);
int  __stdcall EU_GetDropdownSelected(HWND hwnd, int element_id);
void __stdcall EU_SetDropdownOpen(HWND hwnd, int element_id, int open);
int  __stdcall EU_GetDropdownOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetDropdownItemCount(HWND hwnd, int element_id);
void __stdcall EU_SetDropdownDisabled(HWND hwnd, int element_id, const int* indices, int count);
int  __stdcall EU_GetDropdownState(HWND hwnd, int element_id,
                                   int* selected_index, int* item_count,
                                   int* disabled_count, int* selected_level,
                                   int* hover_index);
void __stdcall EU_SetDropdownOptions(HWND hwnd, int element_id,
                                     int trigger_mode, int hide_on_click,
                                     int split_button, int button_variant,
                                     int size, int trigger_style);
int  __stdcall EU_GetDropdownOptions(HWND hwnd, int element_id,
                                     int* trigger_mode, int* hide_on_click,
                                     int* split_button, int* button_variant,
                                     int* size, int* trigger_style);
void __stdcall EU_SetDropdownItemMeta(HWND hwnd, int element_id,
                                      const unsigned char* icons_bytes, int icons_len,
                                      const unsigned char* commands_bytes, int commands_len,
                                      const int* divided_indices, int divided_count);
int  __stdcall EU_GetDropdownItemMeta(HWND hwnd, int element_id, int item_index,
                                      unsigned char* icon_buffer, int icon_buffer_size,
                                      unsigned char* command_buffer, int command_buffer_size,
                                      int* divided, int* disabled, int* level);
void __stdcall EU_SetDropdownCommandCallback(HWND hwnd, int element_id, DropdownCommandCallback cb);
void __stdcall EU_SetDropdownMainClickCallback(HWND hwnd, int element_id, ElementClickCallback cb);
void __stdcall EU_SetMenuItems(HWND hwnd, int element_id,
                               const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetMenuActive(HWND hwnd, int element_id, int active_index);
int  __stdcall EU_GetMenuActive(HWND hwnd, int element_id);
void __stdcall EU_SetMenuOrientation(HWND hwnd, int element_id, int orientation);
int  __stdcall EU_GetMenuOrientation(HWND hwnd, int element_id);
int  __stdcall EU_GetMenuItemCount(HWND hwnd, int element_id);
void __stdcall EU_SetMenuExpanded(HWND hwnd, int element_id, const int* indices, int count);
int  __stdcall EU_GetMenuState(HWND hwnd, int element_id,
                               int* active_index, int* item_count,
                               int* orientation, int* active_level,
                               int* visible_count, int* expanded_count,
                               int* hover_index);
int  __stdcall EU_GetMenuActivePath(HWND hwnd, int element_id,
                                    unsigned char* buffer, int buffer_size);
void __stdcall EU_SetMenuColors(HWND hwnd, int element_id,
                                Color bg, Color text_color, Color active_text_color,
                                Color hover_bg, Color disabled_text_color, Color border);
int  __stdcall EU_GetMenuColors(HWND hwnd, int element_id,
                                Color* bg, Color* text_color, Color* active_text_color,
                                Color* hover_bg, Color* disabled_text_color, Color* border);
void __stdcall EU_SetMenuCollapsed(HWND hwnd, int element_id, int collapsed);
int  __stdcall EU_GetMenuCollapsed(HWND hwnd, int element_id);
void __stdcall EU_SetMenuItemMeta(HWND hwnd, int element_id,
                                  const unsigned char* icons_bytes, int icons_len,
                                  const int* group_indices, int group_count,
                                  const unsigned char* hrefs_bytes, int hrefs_len,
                                  const unsigned char* targets_bytes, int targets_len,
                                  const unsigned char* commands_bytes, int commands_len);
int  __stdcall EU_GetMenuItemMeta(HWND hwnd, int element_id, int item_index,
                                  unsigned char* icon_buffer, int icon_buffer_size,
                                  unsigned char* href_buffer, int href_buffer_size,
                                  unsigned char* target_buffer, int target_buffer_size,
                                  unsigned char* command_buffer, int command_buffer_size,
                                  int* is_group, int* disabled, int* level);
void __stdcall EU_SetMenuSelectCallback(HWND hwnd, int element_id, MenuSelectCallback cb);
void __stdcall EU_SetAnchorItems(HWND hwnd, int element_id,
                                 const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetAnchorActive(HWND hwnd, int element_id, int active_index);
int  __stdcall EU_GetAnchorActive(HWND hwnd, int element_id);
int  __stdcall EU_GetAnchorItemCount(HWND hwnd, int element_id);
void __stdcall EU_SetAnchorTargets(HWND hwnd, int element_id, const int* positions, int count);
void __stdcall EU_SetAnchorOptions(HWND hwnd, int element_id, int scroll_offset, int target_container_id);
void __stdcall EU_SetAnchorScroll(HWND hwnd, int element_id, int scroll_position);
int  __stdcall EU_GetAnchorState(HWND hwnd, int element_id,
                                 int* active_index, int* item_count,
                                 int* scroll_position, int* offset,
                                 int* target_position, int* container_id,
                                 int* hover_index);
void __stdcall EU_SetBacktopState(HWND hwnd, int element_id, int scroll_position, int threshold, int target_position);
int  __stdcall EU_GetBacktopVisible(HWND hwnd, int element_id);
int  __stdcall EU_GetBacktopState(HWND hwnd, int element_id,
                                  int* scroll_position, int* threshold, int* target_position);
void __stdcall EU_SetBacktopOptions(HWND hwnd, int element_id,
                                    int scroll_position, int threshold,
                                    int target_position, int container_id,
                                    int duration_ms);
void __stdcall EU_SetBacktopScroll(HWND hwnd, int element_id, int scroll_position);
void __stdcall EU_TriggerBacktop(HWND hwnd, int element_id);
int  __stdcall EU_GetBacktopFullState(HWND hwnd, int element_id,
                                      int* scroll_position, int* threshold,
                                      int* target_position, int* container_id,
                                      int* visible, int* duration_ms,
                                      int* last_scroll_before_jump,
                                      int* activated_count);
void __stdcall EU_SetSegmentedItems(HWND hwnd, int element_id,
                                    const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetSegmentedActive(HWND hwnd, int element_id, int active_index);
int  __stdcall EU_GetSegmentedActive(HWND hwnd, int element_id);
int  __stdcall EU_GetSegmentedItemCount(HWND hwnd, int element_id);
void __stdcall EU_SetSegmentedDisabled(HWND hwnd, int element_id, const int* indices, int count);
int  __stdcall EU_GetSegmentedState(HWND hwnd, int element_id,
                                    int* active_index, int* item_count,
                                    int* disabled_count, int* hover_index);
void __stdcall EU_SetPageHeaderText(HWND hwnd, int element_id,
                                    const unsigned char* title_bytes, int title_len,
                                    const unsigned char* subtitle_bytes, int subtitle_len);
void __stdcall EU_SetPageHeaderBreadcrumbs(HWND hwnd, int element_id,
                                           const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetPageHeaderActions(HWND hwnd, int element_id,
                                       const unsigned char* items_bytes, int items_len);
int  __stdcall EU_GetPageHeaderAction(HWND hwnd, int element_id);
void __stdcall EU_SetPageHeaderBackText(HWND hwnd, int element_id,
                                        const unsigned char* back_bytes, int back_len);
void __stdcall EU_SetPageHeaderActiveAction(HWND hwnd, int element_id, int action_index);
void __stdcall EU_SetPageHeaderBreadcrumbActive(HWND hwnd, int element_id, int breadcrumb_index);
void __stdcall EU_TriggerPageHeaderBack(HWND hwnd, int element_id);
void __stdcall EU_ResetPageHeaderResult(HWND hwnd, int element_id);
int  __stdcall EU_GetPageHeaderState(HWND hwnd, int element_id,
                                     int* active_action, int* action_count,
                                     int* active_breadcrumb, int* breadcrumb_count,
                                     int* back_clicked_count,
                                     int* back_hovered, int* action_hover,
                                     int* breadcrumb_hover);
void __stdcall EU_SetAffixText(HWND hwnd, int element_id,
                               const unsigned char* title_bytes, int title_len,
                               const unsigned char* body_bytes, int body_len);
void __stdcall EU_SetAffixState(HWND hwnd, int element_id, int scroll_position, int offset);
int  __stdcall EU_GetAffixFixed(HWND hwnd, int element_id);
int  __stdcall EU_GetAffixState(HWND hwnd, int element_id,
                                int* scroll_position, int* offset, int* fixed);
void __stdcall EU_SetAffixOptions(HWND hwnd, int element_id,
                                  int scroll_position, int offset, int container_id,
                                  int placeholder_height, int z_index);
int  __stdcall EU_GetAffixOptions(HWND hwnd, int element_id,
                                  int* scroll_position, int* offset, int* fixed,
                                  int* container_id, int* placeholder_height,
                                  int* fixed_top, int* z_index);
void __stdcall EU_SetWatermarkContent(HWND hwnd, int element_id,
                                      const unsigned char* content_bytes, int content_len);
void __stdcall EU_SetWatermarkOptions(HWND hwnd, int element_id,
                                      int gap_x, int gap_y, int rotation_degrees, int alpha);
int  __stdcall EU_GetWatermarkOptions(HWND hwnd, int element_id,
                                      int* gap_x, int* gap_y, int* rotation_degrees, int* alpha);
void __stdcall EU_SetWatermarkLayer(HWND hwnd, int element_id,
                                    int container_id, int overlay, int pass_through, int z_index);
int  __stdcall EU_GetWatermarkFullOptions(HWND hwnd, int element_id,
                                          int* gap_x, int* gap_y, int* rotation_degrees, int* alpha,
                                          int* container_id, int* overlay, int* pass_through,
                                          int* z_index, int* tile_count_x, int* tile_count_y);
void __stdcall EU_SetTourSteps(HWND hwnd, int element_id,
                               const unsigned char* steps_bytes, int steps_len);
void __stdcall EU_SetTourActive(HWND hwnd, int element_id, int active_index);
void __stdcall EU_SetTourOpen(HWND hwnd, int element_id, int open);
void __stdcall EU_SetTourOptions(HWND hwnd, int element_id,
                                 int open, int mask,
                                 int target_x, int target_y, int target_w, int target_h);
void __stdcall EU_SetTourTargetElement(HWND hwnd, int element_id, int target_element_id, int padding);
void __stdcall EU_SetTourMaskBehavior(HWND hwnd, int element_id, int pass_through, int close_on_mask);
int  __stdcall EU_GetTourActive(HWND hwnd, int element_id);
int  __stdcall EU_GetTourOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetTourStepCount(HWND hwnd, int element_id);
int  __stdcall EU_GetTourOptions(HWND hwnd, int element_id,
                                 int* open, int* mask,
                                 int* target_x, int* target_y, int* target_w, int* target_h);
int  __stdcall EU_GetTourFullState(HWND hwnd, int element_id,
                                   int* active_index, int* step_count,
                                   int* open, int* mask,
                                   int* target_x, int* target_y, int* target_w, int* target_h,
                                   int* target_element_id, int* mask_passthrough,
                                   int* close_on_mask, int* last_action, int* change_count);
void __stdcall EU_SetImageSource(HWND hwnd, int element_id,
                                 const unsigned char* src_bytes, int src_len,
                                 const unsigned char* alt_bytes, int alt_len);
void __stdcall EU_SetImageFit(HWND hwnd, int element_id, int fit);
void __stdcall EU_SetImagePreview(HWND hwnd, int element_id, int open);
void __stdcall EU_SetImagePreviewEnabled(HWND hwnd, int element_id, int enabled);
void __stdcall EU_SetImagePreviewTransform(HWND hwnd, int element_id,
                                           int scale_percent, int offset_x, int offset_y);
void __stdcall EU_SetImageCacheEnabled(HWND hwnd, int element_id, int enabled);
void __stdcall EU_SetImageLazy(HWND hwnd, int element_id, int lazy);
void __stdcall EU_SetImagePlaceholder(HWND hwnd, int element_id,
                                      const unsigned char* icon_bytes, int icon_len,
                                      const unsigned char* text_bytes, int text_len,
                                      Color fg, Color bg);
void __stdcall EU_SetImageErrorContent(HWND hwnd, int element_id,
                                       const unsigned char* icon_bytes, int icon_len,
                                       const unsigned char* text_bytes, int text_len,
                                       Color fg, Color bg);
void __stdcall EU_SetImagePreviewList(HWND hwnd, int element_id,
                                      const unsigned char* sources_bytes, int sources_len,
                                      int selected_index);
void __stdcall EU_SetImagePreviewIndex(HWND hwnd, int element_id, int index);
int  __stdcall EU_GetImageStatus(HWND hwnd, int element_id);
int  __stdcall EU_GetImagePreviewOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetImageOptions(HWND hwnd, int element_id,
                                  int* fit, int* preview_enabled, int* preview_open, int* status);
int  __stdcall EU_GetImageFullOptions(HWND hwnd, int element_id,
                                      int* fit, int* preview_enabled, int* preview_open, int* status,
                                      int* scale_percent, int* offset_x, int* offset_y,
                                      int* cache_enabled, int* reload_count,
                                      int* bitmap_width, int* bitmap_height);
int  __stdcall EU_GetImageAdvancedOptions(HWND hwnd, int element_id,
                                          int* fit, int* lazy, int* preview_enabled,
                                          int* preview_open, int* preview_index,
                                          int* preview_count, int* status,
                                          int* scale_percent, int* offset_x, int* offset_y);
void __stdcall EU_SetCarouselItems(HWND hwnd, int element_id,
                                   const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetCarouselActive(HWND hwnd, int element_id, int active_index);
void __stdcall EU_SetCarouselOptions(HWND hwnd, int element_id,
                                     int loop, int indicator_position,
                                     int show_arrows, int show_indicators);
void __stdcall EU_SetCarouselAutoplay(HWND hwnd, int element_id, int enabled, int interval_ms);
void __stdcall EU_SetCarouselAnimation(HWND hwnd, int element_id, int transition_ms);
void __stdcall EU_CarouselAdvance(HWND hwnd, int element_id, int delta);
void __stdcall EU_CarouselTick(HWND hwnd, int element_id, int elapsed_ms);
int  __stdcall EU_GetCarouselActive(HWND hwnd, int element_id);
int  __stdcall EU_GetCarouselItemCount(HWND hwnd, int element_id);
int  __stdcall EU_GetCarouselOptions(HWND hwnd, int element_id,
                                     int* loop, int* indicator_position,
                                     int* show_arrows, int* show_indicators,
                                     int* autoplay, int* interval_ms);
int  __stdcall EU_GetCarouselFullState(HWND hwnd, int element_id,
                                       int* active_index, int* previous_index,
                                       int* item_count, int* loop,
                                       int* indicator_position,
                                       int* show_arrows, int* show_indicators,
                                       int* autoplay, int* interval_ms,
                                       int* autoplay_tick, int* autoplay_elapsed_ms,
                                       int* transition_ms, int* transition_progress,
                                       int* transition_direction,
                                       int* last_action, int* change_count);
void __stdcall EU_SetUploadFiles(HWND hwnd, int element_id,
                                 const unsigned char* files_bytes, int files_len);
void __stdcall EU_SetUploadFileItems(HWND hwnd, int element_id,
                                     const unsigned char* files_bytes, int files_len);
void __stdcall EU_SetUploadOptions(HWND hwnd, int element_id, int multiple, int auto_upload);
void __stdcall EU_SetUploadStyle(HWND hwnd, int element_id, int style_mode,
                                 int show_file_list, int show_tip, int show_actions,
                                 int drop_enabled);
int  __stdcall EU_GetUploadStyle(HWND hwnd, int element_id, int* style_mode,
                                 int* show_file_list, int* show_tip,
                                 int* show_actions, int* drop_enabled);
void __stdcall EU_SetUploadTexts(HWND hwnd, int element_id,
                                 const unsigned char* title_bytes, int title_len,
                                 const unsigned char* tip_bytes, int tip_len,
                                 const unsigned char* trigger_bytes, int trigger_len,
                                 const unsigned char* submit_bytes, int submit_len);
void __stdcall EU_SetUploadConstraints(HWND hwnd, int element_id, int limit,
                                       int max_size_kb,
                                       const unsigned char* accept_bytes, int accept_len);
int  __stdcall EU_GetUploadConstraints(HWND hwnd, int element_id, int* limit,
                                       int* max_size_kb,
                                       unsigned char* accept_buffer, int accept_buffer_size);
void __stdcall EU_SetUploadPreviewOpen(HWND hwnd, int element_id, int file_index, int open);
int  __stdcall EU_GetUploadPreviewState(HWND hwnd, int element_id, int* file_index, int* open);
void __stdcall EU_SetUploadSelectedFiles(HWND hwnd, int element_id,
                                         const unsigned char* files_bytes, int files_len);
void __stdcall EU_SetUploadFileStatus(HWND hwnd, int element_id,
                                      int file_index, int status, int progress);
void __stdcall EU_RemoveUploadFile(HWND hwnd, int element_id, int file_index);
void __stdcall EU_RetryUploadFile(HWND hwnd, int element_id, int file_index);
void __stdcall EU_ClearUploadFiles(HWND hwnd, int element_id);
int  __stdcall EU_OpenUploadFileDialog(HWND hwnd, int element_id);
int  __stdcall EU_StartUpload(HWND hwnd, int element_id, int file_index);
int  __stdcall EU_GetUploadFileCount(HWND hwnd, int element_id);
int  __stdcall EU_GetUploadFileStatus(HWND hwnd, int element_id,
                                      int file_index, int* status, int* progress);
int  __stdcall EU_GetUploadSelectedFiles(HWND hwnd, int element_id,
                                         unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetUploadFileName(HWND hwnd, int element_id, int file_index,
                                    unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetUploadFullState(HWND hwnd, int element_id,
                                     int* file_count, int* selected_count,
                                     int* last_selected_count, int* upload_request_count,
                                     int* retry_count, int* remove_count,
                                     int* last_action, int* waiting_count,
                                     int* uploading_count, int* success_count,
                                     int* failed_count, int* multiple,
                                     int* auto_upload);
void __stdcall EU_SetUploadSelectCallback(HWND hwnd, int element_id, ElementTextCallback cb);
void __stdcall EU_SetUploadActionCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetInfiniteScrollItems(HWND hwnd, int element_id,
                                         const unsigned char* items_bytes, int items_len);
void __stdcall EU_AppendInfiniteScrollItems(HWND hwnd, int element_id,
                                            const unsigned char* items_bytes, int items_len);
void __stdcall EU_ClearInfiniteScrollItems(HWND hwnd, int element_id);
void __stdcall EU_SetInfiniteScrollState(HWND hwnd, int element_id,
                                         int loading, int no_more, int disabled);
void __stdcall EU_SetInfiniteScrollOptions(HWND hwnd, int element_id,
                                           int item_height, int gap, int threshold,
                                           int style_mode, int show_scrollbar, int show_index);
void __stdcall EU_SetInfiniteScrollTexts(HWND hwnd, int element_id,
                                         const unsigned char* loading_bytes, int loading_len,
                                         const unsigned char* no_more_bytes, int no_more_len,
                                         const unsigned char* empty_bytes, int empty_len);
void __stdcall EU_SetInfiniteScrollScroll(HWND hwnd, int element_id, int scroll_y);
int  __stdcall EU_GetInfiniteScrollFullState(HWND hwnd, int element_id,
                                             int* item_count, int* scroll_y, int* max_scroll,
                                             int* content_height, int* viewport_height,
                                             int* loading, int* no_more, int* disabled,
                                             int* load_count, int* change_count,
                                             int* last_action, int* threshold,
                                             int* style_mode, int* show_scrollbar,
                                             int* show_index);
void __stdcall EU_SetInfiniteScrollLoadCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetBreadcrumbItems(HWND hwnd, int element_id,
                                     const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetBreadcrumbSeparator(HWND hwnd, int element_id,
                                         const unsigned char* separator_bytes, int separator_len);
void __stdcall EU_SetBreadcrumbCurrent(HWND hwnd, int element_id, int current_index);
void __stdcall EU_TriggerBreadcrumbClick(HWND hwnd, int element_id, int item_index);
int  __stdcall EU_GetBreadcrumbCurrent(HWND hwnd, int element_id);
int  __stdcall EU_GetBreadcrumbItemCount(HWND hwnd, int element_id);
int  __stdcall EU_GetBreadcrumbState(HWND hwnd, int element_id,
                                     int* current_index, int* item_count);
int  __stdcall EU_GetBreadcrumbItem(HWND hwnd, int element_id, int item_index,
                                    unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetBreadcrumbFullState(HWND hwnd, int element_id,
                                         int* current_index, int* item_count,
                                         int* hover_index, int* press_index,
                                         int* last_clicked_index,
                                         int* click_count, int* last_action);
void __stdcall EU_SetBreadcrumbSelectCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetTabsItems(HWND hwnd, int element_id,
                               const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetTabsItemsEx(HWND hwnd, int element_id,
                                 const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetTabsActive(HWND hwnd, int element_id, int active_index);
void __stdcall EU_SetTabsActiveName(HWND hwnd, int element_id,
                                    const unsigned char* name_bytes, int name_len);
void __stdcall EU_SetTabsType(HWND hwnd, int element_id, int tab_type);
void __stdcall EU_SetTabsPosition(HWND hwnd, int element_id, int tab_position);
void __stdcall EU_SetTabsOptions(HWND hwnd, int element_id,
                                 int tab_type, int closable, int addable);
void __stdcall EU_SetTabsEditable(HWND hwnd, int element_id, int editable);
void __stdcall EU_SetTabsContentVisible(HWND hwnd, int element_id, int visible);
void __stdcall EU_AddTabsItem(HWND hwnd, int element_id,
                              const unsigned char* text_bytes, int text_len);
void __stdcall EU_CloseTabsItem(HWND hwnd, int element_id, int item_index);
void __stdcall EU_SetTabsScroll(HWND hwnd, int element_id, int offset);
void __stdcall EU_TabsScroll(HWND hwnd, int element_id, int delta);
int  __stdcall EU_GetTabsActive(HWND hwnd, int element_id);
int  __stdcall EU_GetTabsItemCount(HWND hwnd, int element_id);
int  __stdcall EU_GetTabsState(HWND hwnd, int element_id,
                               int* active_index, int* item_count, int* tab_type);
int  __stdcall EU_GetTabsItem(HWND hwnd, int element_id, int item_index,
                              unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetTabsActiveName(HWND hwnd, int element_id,
                                    unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetTabsItemContent(HWND hwnd, int element_id, int item_index,
                                     unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetTabsFullState(HWND hwnd, int element_id,
                                   int* active_index, int* item_count, int* tab_type,
                                   int* closable, int* addable,
                                   int* scroll_offset, int* max_scroll_offset,
                                   int* hover_index, int* press_index,
                                   int* hover_part, int* press_part,
                                   int* last_closed_index, int* last_added_index,
                                   int* close_count, int* add_count,
                                   int* select_count, int* scroll_count,
                                   int* last_action);
int  __stdcall EU_GetTabsFullStateEx(HWND hwnd, int element_id,
                                     int* active_index, int* item_count, int* tab_type,
                                     int* closable, int* addable,
                                     int* scroll_offset, int* max_scroll_offset,
                                     int* hover_index, int* press_index,
                                     int* hover_part, int* press_part,
                                     int* last_closed_index, int* last_added_index,
                                     int* close_count, int* add_count,
                                     int* select_count, int* scroll_count,
                                     int* last_action, int* tab_position,
                                     int* editable, int* content_visible,
                                     int* active_disabled, int* active_closable);
void __stdcall EU_SetTabsChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetTabsCloseCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetTabsAddCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetPagination(HWND hwnd, int element_id,
                                int total, int page_size, int current_page);
void __stdcall EU_SetPaginationCurrent(HWND hwnd, int element_id, int current_page);
void __stdcall EU_SetPaginationPageSize(HWND hwnd, int element_id, int page_size);
void __stdcall EU_SetPaginationOptions(HWND hwnd, int element_id,
                                       int show_jumper, int show_size_changer,
                                       int visible_page_count);
void __stdcall EU_SetPaginationPageSizeOptions(HWND hwnd, int element_id,
                                               const int* sizes, int count);
void __stdcall EU_SetPaginationJumpPage(HWND hwnd, int element_id, int jump_page);
void __stdcall EU_TriggerPaginationJump(HWND hwnd, int element_id);
void __stdcall EU_NextPaginationPageSize(HWND hwnd, int element_id);
int  __stdcall EU_GetPaginationCurrent(HWND hwnd, int element_id);
int  __stdcall EU_GetPaginationPageCount(HWND hwnd, int element_id);
int  __stdcall EU_GetPaginationState(HWND hwnd, int element_id,
                                     int* total, int* page_size,
                                     int* current_page, int* page_count);
int  __stdcall EU_GetPaginationFullState(HWND hwnd, int element_id,
                                         int* total, int* page_size,
                                         int* current_page, int* page_count,
                                         int* jump_page, int* visible_page_count,
                                         int* show_jumper, int* show_size_changer,
                                         int* hover_part, int* press_part,
                                         int* change_count, int* size_change_count,
                                         int* jump_count, int* last_action);
void __stdcall EU_SetPaginationChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetStepsItems(HWND hwnd, int element_id,
                                const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetStepsDetailItems(HWND hwnd, int element_id,
                                      const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetStepsIconItems(HWND hwnd, int element_id,
                                    const unsigned char* items_bytes, int items_len);
void __stdcall EU_SetStepsActive(HWND hwnd, int element_id, int active_index);
void __stdcall EU_SetStepsDirection(HWND hwnd, int element_id, int direction);
void __stdcall EU_SetStepsOptions(HWND hwnd, int element_id, int space,
                                  int align_center, int simple,
                                  int finish_status, int process_status);
int  __stdcall EU_GetStepsOptions(HWND hwnd, int element_id, int* space,
                                  int* align_center, int* simple,
                                  int* finish_status, int* process_status);
void __stdcall EU_SetStepsStatuses(HWND hwnd, int element_id, const int* statuses, int count);
void __stdcall EU_TriggerStepsClick(HWND hwnd, int element_id, int item_index);
int  __stdcall EU_GetStepsActive(HWND hwnd, int element_id);
int  __stdcall EU_GetStepsItemCount(HWND hwnd, int element_id);
int  __stdcall EU_GetStepsState(HWND hwnd, int element_id,
                                int* active_index, int* item_count, int* direction);
int  __stdcall EU_GetStepsItem(HWND hwnd, int element_id, int item_index, int text_kind,
                               unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetStepsFullState(HWND hwnd, int element_id,
                                    int* active_index, int* item_count, int* direction,
                                   int* hover_index, int* press_index,
                                   int* last_clicked_index, int* click_count,
                                   int* change_count, int* last_action,
                                   int* active_status, int* failed_count);
int  __stdcall EU_GetStepsVisualState(HWND hwnd, int element_id,
                                      int* space, int* align_center, int* simple,
                                      int* finish_status, int* process_status,
                                      int* icon_count);
void __stdcall EU_SetStepsChangeCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetAlertDescription(HWND hwnd, int element_id,
                                      const unsigned char* desc_bytes, int desc_len);
void __stdcall EU_SetAlertType(HWND hwnd, int element_id, int alert_type);
void __stdcall EU_SetAlertEffect(HWND hwnd, int element_id, int effect);
void __stdcall EU_SetAlertClosable(HWND hwnd, int element_id, int closable);
void __stdcall EU_SetAlertClosed(HWND hwnd, int element_id, int closed);
void __stdcall EU_TriggerAlertClose(HWND hwnd, int element_id);
int  __stdcall EU_GetAlertClosed(HWND hwnd, int element_id);
int  __stdcall EU_GetAlertOptions(HWND hwnd, int element_id,
                                  int* alert_type, int* effect,
                                  int* closable, int* closed);
int  __stdcall EU_GetAlertFullState(HWND hwnd, int element_id,
                                    int* alert_type, int* effect,
                                    int* closable, int* closed,
                                    int* close_hover, int* close_down,
                                    int* close_count, int* last_action);
void __stdcall EU_SetAlertCloseCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetResultSubtitle(HWND hwnd, int element_id,
                                    const unsigned char* subtitle_bytes, int subtitle_len);
void __stdcall EU_SetResultType(HWND hwnd, int element_id, int result_type);
void __stdcall EU_SetResultActions(HWND hwnd, int element_id,
                                   const unsigned char* actions_bytes, int actions_len);
int  __stdcall EU_GetResultAction(HWND hwnd, int element_id);
int  __stdcall EU_GetResultOptions(HWND hwnd, int element_id,
                                   int* result_type, int* action_count, int* last_action);
void __stdcall EU_SetResultExtraContent(HWND hwnd, int element_id,
                                        const unsigned char* content_bytes, int content_len);
void __stdcall EU_TriggerResultAction(HWND hwnd, int element_id, int action_index);
int  __stdcall EU_GetResultText(HWND hwnd, int element_id, int text_kind,
                                unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetResultActionText(HWND hwnd, int element_id, int action_index,
                                      unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetResultFullState(HWND hwnd, int element_id,
                                     int* result_type, int* action_count, int* last_action,
                                     int* hover_action, int* press_action,
                                     int* action_click_count, int* last_action_source,
                                     int* has_extra_content);
void __stdcall EU_SetResultActionCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetNotificationBody(HWND hwnd, int element_id,
                                      const unsigned char* body_bytes, int body_len);
void __stdcall EU_SetNotificationType(HWND hwnd, int element_id, int notify_type);
void __stdcall EU_SetNotificationClosable(HWND hwnd, int element_id, int closable);
void __stdcall EU_SetNotificationPlacement(HWND hwnd, int element_id, int placement, int offset);
void __stdcall EU_SetNotificationRichMode(HWND hwnd, int element_id, int rich);
void __stdcall EU_SetNotificationOptions(HWND hwnd, int element_id,
                                         int notify_type, int closable, int duration_ms);
void __stdcall EU_SetNotificationClosed(HWND hwnd, int element_id, int closed);
int  __stdcall EU_GetNotificationClosed(HWND hwnd, int element_id);
int  __stdcall EU_GetNotificationOptions(HWND hwnd, int element_id,
                                         int* notify_type, int* closable,
                                         int* duration_ms, int* closed);
void __stdcall EU_SetNotificationStack(HWND hwnd, int element_id, int stack_index, int stack_gap);
void __stdcall EU_TriggerNotificationClose(HWND hwnd, int element_id);
int  __stdcall EU_GetNotificationText(HWND hwnd, int element_id, int text_kind,
                                      unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetNotificationFullState(HWND hwnd, int element_id,
                                           int* notify_type, int* closable,
                                           int* duration_ms, int* closed,
                                           int* close_hover, int* close_down,
                                           int* close_count, int* last_action,
                                           int* timer_elapsed_ms, int* timer_running,
                                           int* stack_index, int* stack_gap);
int  __stdcall EU_GetNotificationFullStateEx(HWND hwnd, int element_id,
                                             int* notify_type, int* closable,
                                             int* duration_ms, int* closed,
                                             int* close_hover, int* close_down,
                                             int* close_count, int* last_action,
                                             int* timer_elapsed_ms, int* timer_running,
                                             int* stack_index, int* stack_gap,
                                             int* placement, int* offset, int* rich);
void __stdcall EU_SetNotificationCloseCallback(HWND hwnd, int element_id, ElementValueCallback cb);

void __stdcall EU_SetMessageText(HWND hwnd, int element_id, const unsigned char* bytes, int len);
void __stdcall EU_SetMessageOptions(HWND hwnd, int element_id, int message_type,
                                    int closable, int center, int rich,
                                    int duration_ms, int offset);
void __stdcall EU_SetMessageClosed(HWND hwnd, int element_id, int closed);
int  __stdcall EU_GetMessageOptions(HWND hwnd, int element_id, int* message_type,
                                    int* closable, int* center, int* rich,
                                    int* duration_ms, int* closed, int* offset);
int  __stdcall EU_GetMessageFullState(HWND hwnd, int element_id, int* message_type,
                                      int* closable, int* center, int* rich,
                                      int* duration_ms, int* closed,
                                      int* close_hover, int* close_down,
                                      int* close_count, int* last_action,
                                      int* timer_elapsed_ms, int* timer_running,
                                      int* stack_index, int* stack_gap, int* offset);
void __stdcall EU_TriggerMessageClose(HWND hwnd, int element_id);
void __stdcall EU_SetMessageCloseCallback(HWND hwnd, int element_id, ElementValueCallback cb);

void __stdcall EU_SetMessageBoxBeforeClose(HWND hwnd, int element_id,
                                           int delay_ms,
                                           const unsigned char* loading_bytes, int loading_len);
void __stdcall EU_SetMessageBoxInput(HWND hwnd, int element_id,
                                     const unsigned char* value_bytes, int value_len,
                                     const unsigned char* placeholder_bytes, int placeholder_len,
                                     const unsigned char* pattern_bytes, int pattern_len,
                                     const unsigned char* error_bytes, int error_len);
int  __stdcall EU_GetMessageBoxInput(HWND hwnd, int element_id,
                                     unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetMessageBoxFullState(HWND hwnd, int element_id,
                                         int* box_type, int* show_cancel, int* center,
                                         int* rich, int* distinguish, int* prompt,
                                         int* confirm_loading, int* input_error_visible,
                                         int* last_action, int* timer_elapsed_ms);
void __stdcall EU_SetLoadingActive(HWND hwnd, int element_id, int active);
void __stdcall EU_SetLoadingOptions(HWND hwnd, int element_id,
                                    int active, int fullscreen, int progress);
int  __stdcall EU_GetLoadingActive(HWND hwnd, int element_id);
int  __stdcall EU_GetLoadingOptions(HWND hwnd, int element_id,
                                    int* active, int* fullscreen, int* progress);
void __stdcall EU_SetLoadingTarget(HWND hwnd, int element_id, int target_element_id, int padding);
int  __stdcall EU_GetLoadingText(HWND hwnd, int element_id, unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetLoadingFullState(HWND hwnd, int element_id,
                                      int* active, int* fullscreen, int* progress,
                                      int* target_element_id, int* target_padding,
                                      int* animation_angle, int* tick_count,
                                      int* timer_running, int* last_action);
void __stdcall EU_SetDialogOpen(HWND hwnd, int element_id, int open);
void __stdcall EU_SetDialogTitle(HWND hwnd, int element_id,
                                 const unsigned char* title_bytes, int title_len);
void __stdcall EU_SetDialogBody(HWND hwnd, int element_id,
                                const unsigned char* body_bytes, int body_len);
void __stdcall EU_SetDialogOptions(HWND hwnd, int element_id, int open, int modal,
                                   int closable, int close_on_mask, int draggable,
                                   int w, int h);
void __stdcall EU_SetDialogAdvancedOptions(HWND hwnd, int element_id,
                                           int width_mode, int width_value,
                                           int center, int footer_center,
                                           int content_padding, int footer_height);
int  __stdcall EU_GetDialogAdvancedOptions(HWND hwnd, int element_id,
                                           int* width_mode, int* width_value,
                                           int* center, int* footer_center,
                                           int* content_padding, int* footer_height,
                                           int* content_parent_id, int* footer_parent_id,
                                           int* close_pending);
int  __stdcall EU_GetDialogContentParent(HWND hwnd, int element_id);
int  __stdcall EU_GetDialogFooterParent(HWND hwnd, int element_id);
void __stdcall EU_SetDialogBeforeCloseCallback(HWND hwnd, int element_id,
                                               ElementBeforeCloseCallback cb);
void __stdcall EU_ConfirmDialogClose(HWND hwnd, int element_id, int allow);
int  __stdcall EU_GetDialogOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetDialogOptions(HWND hwnd, int element_id,
                                   int* open, int* modal, int* closable,
                                   int* close_on_mask, int* draggable,
                                   int* w, int* h);
void __stdcall EU_SetDialogButtons(HWND hwnd, int element_id,
                                   const unsigned char* buttons_bytes, int buttons_len);
void __stdcall EU_TriggerDialogButton(HWND hwnd, int element_id, int button_index);
int  __stdcall EU_GetDialogText(HWND hwnd, int element_id, int text_kind,
                                unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetDialogButtonText(HWND hwnd, int element_id, int button_index,
                                      unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetDialogFullState(HWND hwnd, int element_id,
                                     int* open, int* modal, int* closable,
                                     int* close_on_mask, int* draggable,
                                     int* w, int* h, int* button_count,
                                     int* active_button, int* last_button,
                                     int* button_click_count, int* close_count,
                                     int* last_action, int* offset_x, int* offset_y,
                                     int* hover_part, int* press_part);
void __stdcall EU_SetDialogButtonCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetDrawerOpen(HWND hwnd, int element_id, int open);
void __stdcall EU_SetDrawerTitle(HWND hwnd, int element_id,
                                 const unsigned char* title_bytes, int title_len);
void __stdcall EU_SetDrawerBody(HWND hwnd, int element_id,
                                const unsigned char* body_bytes, int body_len);
void __stdcall EU_SetDrawerPlacement(HWND hwnd, int element_id, int placement);
void __stdcall EU_SetDrawerOptions(HWND hwnd, int element_id, int placement, int open,
                                   int modal, int closable, int close_on_mask, int size);
void __stdcall EU_SetDrawerAdvancedOptions(HWND hwnd, int element_id,
                                           int show_header, int show_close,
                                           int close_on_escape, int content_padding,
                                           int footer_height, int size_mode,
                                           int size_value);
int  __stdcall EU_GetDrawerAdvancedOptions(HWND hwnd, int element_id,
                                           int* show_header, int* show_close,
                                           int* close_on_escape, int* content_padding,
                                           int* footer_height, int* size_mode,
                                           int* size_value, int* content_parent_id,
                                           int* footer_parent_id, int* close_pending);
int  __stdcall EU_GetDrawerContentParent(HWND hwnd, int element_id);
int  __stdcall EU_GetDrawerFooterParent(HWND hwnd, int element_id);
void __stdcall EU_SetDrawerBeforeCloseCallback(HWND hwnd, int element_id,
                                               ElementBeforeCloseCallback cb);
void __stdcall EU_ConfirmDrawerClose(HWND hwnd, int element_id, int allow);
int  __stdcall EU_GetDrawerOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetDrawerOptions(HWND hwnd, int element_id,
                                   int* placement, int* open, int* modal,
                                   int* closable, int* close_on_mask, int* size);
void __stdcall EU_SetDrawerAnimation(HWND hwnd, int element_id, int duration_ms);
void __stdcall EU_TriggerDrawerClose(HWND hwnd, int element_id);
int  __stdcall EU_GetDrawerText(HWND hwnd, int element_id, int text_kind,
                                unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetDrawerFullState(HWND hwnd, int element_id,
                                     int* placement, int* open, int* modal,
                                     int* closable, int* close_on_mask, int* size,
                                     int* animation_progress, int* animation_ms,
                                     int* tick_count, int* timer_running,
                                     int* close_count, int* last_action,
                                     int* hover_part, int* press_part);
void __stdcall EU_SetDrawerCloseCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetTooltipContent(HWND hwnd, int element_id,
                                    const unsigned char* content_bytes, int content_len);
void __stdcall EU_SetTooltipOpen(HWND hwnd, int element_id, int open);
void __stdcall EU_SetTooltipOptions(HWND hwnd, int element_id, int placement, int open, int max_width);
int  __stdcall EU_GetTooltipOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetTooltipOptions(HWND hwnd, int element_id,
                                    int* placement, int* open, int* max_width);
void __stdcall EU_SetTooltipBehavior(HWND hwnd, int element_id,
                                     int show_delay, int hide_delay,
                                     int trigger_mode, int show_arrow);
void __stdcall EU_SetTooltipAdvancedOptions(HWND hwnd, int element_id,
                                            int placement, int effect,
                                            int disabled, int show_arrow,
                                            int offset, int max_width);
int  __stdcall EU_GetTooltipAdvancedOptions(HWND hwnd, int element_id,
                                            int* placement, int* effect,
                                            int* disabled, int* show_arrow,
                                            int* offset, int* max_width);
void __stdcall EU_TriggerTooltip(HWND hwnd, int element_id, int open);
int  __stdcall EU_GetTooltipText(HWND hwnd, int element_id, int text_kind,
                                 unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetTooltipFullState(HWND hwnd, int element_id,
                                      int* placement, int* open, int* max_width,
                                      int* show_arrow, int* show_delay,
                                      int* hide_delay, int* trigger_mode,
                                      int* timer_running, int* timer_phase,
                                      int* open_count, int* close_count,
                                      int* last_action, int* popup_x,
                                      int* popup_y, int* popup_w, int* popup_h);
void __stdcall EU_SetPopoverOpen(HWND hwnd, int element_id, int open);
void __stdcall EU_SetPopoverContent(HWND hwnd, int element_id,
                                    const unsigned char* content_bytes, int content_len);
void __stdcall EU_SetPopoverTitle(HWND hwnd, int element_id,
                                  const unsigned char* title_bytes, int title_len);
void __stdcall EU_SetPopoverOptions(HWND hwnd, int element_id, int placement, int open,
                                    int popup_width, int popup_height, int closable);
void __stdcall EU_SetPopoverAdvancedOptions(HWND hwnd, int element_id,
                                            int placement, int open,
                                            int popup_width, int popup_height,
                                            int closable);
void __stdcall EU_SetPopoverBehavior(HWND hwnd, int element_id,
                                     int trigger_mode, int close_on_outside,
                                     int show_arrow, int offset);
int  __stdcall EU_GetPopoverBehavior(HWND hwnd, int element_id,
                                     int* trigger_mode, int* close_on_outside,
                                     int* show_arrow, int* offset);
int  __stdcall EU_GetPopoverContentParent(HWND hwnd, int element_id);
int  __stdcall EU_GetPopoverOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetPopoverOptions(HWND hwnd, int element_id,
                                    int* placement, int* open,
                                    int* popup_width, int* popup_height, int* closable);
void __stdcall EU_TriggerPopover(HWND hwnd, int element_id, int open);
int  __stdcall EU_GetPopoverText(HWND hwnd, int element_id, int text_kind,
                                 unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetPopoverFullState(HWND hwnd, int element_id,
                                      int* placement, int* open,
                                      int* popup_width, int* popup_height,
                                      int* closable, int* open_count,
                                      int* close_count, int* last_action,
                                      int* focus_part, int* close_hover,
                                      int* popup_x, int* popup_y,
                                      int* popup_w, int* popup_h);
void __stdcall EU_SetPopoverActionCallback(HWND hwnd, int element_id, ElementValueCallback cb);
void __stdcall EU_SetPopconfirmOpen(HWND hwnd, int element_id, int open);
void __stdcall EU_SetPopconfirmOptions(HWND hwnd, int element_id, int placement, int open,
                                       int popup_width, int popup_height);
void __stdcall EU_SetPopconfirmAdvancedOptions(HWND hwnd, int element_id,
                                               int placement, int open,
                                               int popup_width, int popup_height,
                                               int trigger_mode, int close_on_outside,
                                               int show_arrow, int offset);
void __stdcall EU_SetPopconfirmContent(HWND hwnd, int element_id,
                                       const unsigned char* title_bytes, int title_len,
                                       const unsigned char* content_bytes, int content_len);
void __stdcall EU_SetPopconfirmButtons(HWND hwnd, int element_id,
                                       const unsigned char* confirm_bytes, int confirm_len,
                                       const unsigned char* cancel_bytes, int cancel_len);
void __stdcall EU_SetPopconfirmIcon(HWND hwnd, int element_id,
                                    const unsigned char* icon_bytes, int icon_len,
                                    Color icon_color, int visible);
int  __stdcall EU_GetPopconfirmIcon(HWND hwnd, int element_id,
                                    unsigned char* buffer, int buffer_size,
                                    Color* icon_color, int* visible);
void __stdcall EU_ResetPopconfirmResult(HWND hwnd, int element_id);
int  __stdcall EU_GetPopconfirmOpen(HWND hwnd, int element_id);
int  __stdcall EU_GetPopconfirmResult(HWND hwnd, int element_id);
int  __stdcall EU_GetPopconfirmOptions(HWND hwnd, int element_id,
                                       int* placement, int* open,
                                       int* popup_width, int* popup_height, int* result);
void __stdcall EU_TriggerPopconfirmResult(HWND hwnd, int element_id, int result);
int  __stdcall EU_GetPopconfirmText(HWND hwnd, int element_id, int text_kind,
                                    unsigned char* buffer, int buffer_size);
int  __stdcall EU_GetPopconfirmFullState(HWND hwnd, int element_id,
                                         int* placement, int* open,
                                         int* popup_width, int* popup_height,
                                         int* result, int* confirm_count,
                                         int* cancel_count, int* result_action,
                                         int* focus_part, int* hover_button,
                                         int* press_button, int* popup_x,
                                         int* popup_y, int* popup_w, int* popup_h);
void __stdcall EU_SetPopconfirmResultCallback(HWND hwnd, int element_id, ElementValueCallback cb);

// ── Callbacks ────────────────────────────────────────────────────────
void __stdcall EU_SetElementClickCallback(HWND hwnd, int element_id, ElementClickCallback cb);
void __stdcall EU_SetElementKeyCallback(HWND hwnd, int element_id, ElementKeyCallback cb);
void __stdcall EU_SetWindowResizeCallback(HWND hwnd, WindowResizeCallback cb);
void __stdcall EU_SetWindowCloseCallback(HWND hwnd, WindowCloseCallback cb);

// ── Theme ────────────────────────────────────────────────────────────
void __stdcall EU_SetDarkMode(HWND hwnd, int dark_mode);
void __stdcall EU_SetThemeMode(HWND hwnd, int mode);
int  __stdcall EU_GetThemeMode(HWND hwnd);
int  __stdcall EU_SetThemeColor(HWND hwnd, const unsigned char* token_bytes, int token_len, Color value);
void __stdcall EU_ResetTheme(HWND hwnd);
